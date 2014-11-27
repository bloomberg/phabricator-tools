"""abd automates the creation and landing of reviews from branches."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_processrepo
#
# Public Functions:
#   create_review
#   create_differential_review
#   update_review
#   update_in_review
#   land
#   create_failed_review
#   try_create_review
#   process_updated_branch
#   process_abandoned_branch
#   process_branches
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlcon_differential

import abdcmnt_commenter
import abdt_conduitgit
import abdt_exception
import abdt_git
import abdt_logging
import abdt_userwarning

_DEFAULT_TEST_PLAN = "I DIDNT TEST"


def create_review(conduit, branch):
    branch.verify_review_branch_base()

    # TODO: we should also cc other users on the branch
    # TODO: if there are emails that don't match up to users then we should
    #       note that on the review and perhaps use the mailer to notify them
    name, email, user, phid = abdt_conduitgit.getPrimaryUserDetailsFromBranch(
        conduit, branch)

    print "- author: " + user

    user_warnings = []

    message = branch.get_commit_message_from_tip()
    parsed = conduit.parse_commit_message(message)

    d = phlcon_differential
    if parsed.errors:
        error_list = phlcon_differential.parse_commit_message_errors(
            parsed.errors)
        for error in error_list:
            if isinstance(error, d.ParseCommitMessageNoTestPlanFail):
                parsed.fields["testPlan"] = _DEFAULT_TEST_PLAN
                user_warnings.append(
                    abdt_userwarning.UsedDefaultTestPlan(_DEFAULT_TEST_PLAN))
            elif isinstance(error, d.ParseCommitMessageUnknownReviewerFail):
                user_warnings.append(
                    abdt_userwarning.UnknownReviewers(
                        error.user_list, message))
            else:
                raise abdt_exception.CommitMessageParseException(
                    errors=parsed.errors,
                    fields=parsed.fields,
                    digest=branch.make_message_digest())

    # remove the author from reviewer list if present
    reviewer_phids_key = phlcon_differential.MessageFields.reviewer_phids
    if reviewer_phids_key in parsed.fields:
        reviewer_phids = parsed.fields[reviewer_phids_key]
        if phid in reviewer_phids:
            reviewer_phids.remove(phid)
            user_warnings.append(abdt_userwarning.SelfReviewer(user, message))

    diff_result = branch.make_raw_diff()
    raw_diff = diff_result.diff

    if not raw_diff:
        raise abdt_exception.AbdUserException("no difference to review")

    if diff_result.reduction_list:
        user_warnings.append(abdt_userwarning.LargeDiff(diff_result))

    revisionid = create_differential_review(
        conduit, user, parsed, branch, raw_diff)

    commenter = abdcmnt_commenter.Commenter(conduit, revisionid)

    if user_warnings:
        commenter.userWarnings(user_warnings)

    abdt_logging.on_review_event(
        'createrev', '{} created {} from {}'.format(
            user, revisionid, branch.review_branch_name()))


def create_differential_review(conduit, user, parsed, branch, raw_diff):
    print "- creating revision"
    revision_id = conduit.create_revision_as_user(
        raw_diff, parsed.fields, user)

    print "- created " + str(revision_id)
    branch.mark_ok_new_review(revision_id)

    print "- commenting on " + str(revision_id)
    commenter = abdcmnt_commenter.Commenter(conduit, revision_id)
    commenter.createdReview(
        branch.get_repo_name(),
        branch.review_branch_hash(),
        branch.review_branch_name(),
        branch.base_branch_name(),
        branch.get_browse_url())

    return revision_id


def update_review(conduit, branch):
    revision_id = branch.review_id_or_none()

    if branch.has_new_commits():
        print "changes on branch"
        branch.verify_review_branch_base()
        update_in_review(conduit, branch)
    elif branch.is_status_bad_abandoned():
        if not conduit.is_review_abandoned(revision_id):
            # update the review as the branch may have been bad previously
            # and we'll want to re-assess it's status
            update_in_review(conduit, branch)
        elif not conduit.is_review_recently_updated(revision_id):
            review_name = branch.review_branch_name()
            review_hash = branch.review_branch_hash()
            branch.remove()
            commenter = abdcmnt_commenter.Commenter(conduit, revision_id)
            commenter.abandonedForUser(
                review_name,
                review_hash,
                abdt_git.ARCYD_ABANDONED_REF)
        return
    elif conduit.is_review_abandoned(revision_id):
        raise abdt_exception.ReviewAbandonedException()
    elif branch.is_status_bad() and not branch.is_status_bad_land():
        try:
            print "try updating bad branch"
            branch.verify_review_branch_base()
            update_in_review(conduit, branch)
        except abdt_exception.AbdUserException:
            print "still bad"

    if not branch.is_status_bad():
        if conduit.is_review_accepted(revision_id):
            branch.verify_review_branch_base()
            land(conduit, branch)
            # TODO: we probably want to do a better job of cleaning up locally
        else:
            print "do nothing"


def update_in_review(conduit, branch):
    print "update_in_review"

    print "- creating diff"
    diff_result = branch.make_raw_diff()

    if not diff_result.diff:
        raise abdt_exception.AbdUserException("no difference to review")

    user_warnings = []
    if diff_result.reduction_list:
        user_warnings.append(abdt_userwarning.LargeDiff(diff_result))

    review_id = branch.review_id_or_none()
    review_id_str = str(review_id)

    print "- updating revision " + review_id_str
    conduit.update_revision(
        review_id,
        diff_result.diff,
        'update\n\n``` lang=text\n' + branch.describe_new_commits() + '```')

    branch.mark_ok_in_review()

    print "- commenting on revision " + review_id_str
    commenter = abdcmnt_commenter.Commenter(conduit, review_id)
    commenter.updatedReview(
        branch.review_branch_hash(),
        branch.review_branch_name())
    if user_warnings:
        commenter.userWarnings(user_warnings)

    abdt_logging.on_review_event(
        'updaterev', '{} updated {}'.format(
            branch.review_branch_name(), review_id))


def land(conduit, branch):
    print "landing " + branch.review_branch_name()

    review_branch_name = branch.review_branch_name()
    base_branch_name = branch.base_branch_name()

    names_emails = branch.get_author_names_emails()
    if not names_emails:
        raise abdt_exception.LandingException(
            "no commits on branch", review_branch_name, base_branch_name)

    # pick the last author as the author for landing
    name, email = names_emails[-1]

    review_id = branch.review_id_or_none()

    # store the branch hash now, the branch will be invalid after landing
    review_branch_hash = branch.review_branch_hash()

    # compose the commit message
    message = conduit.get_commit_message(review_id)

    land_message = branch.land(name, email, message)

    print "- commenting on revision " + str(review_id)
    commenter = abdcmnt_commenter.Commenter(conduit, review_id)
    commenter.landedReview(
        review_branch_hash,
        review_branch_name,
        base_branch_name,
        land_message)

    conduit.close_revision(review_id)

    abdt_logging.on_review_event(
        'landrev', '{} landed {}, {}'.format(
            name, review_id, review_branch_name))


def create_failed_review(conduit, branch, exception):
    user = abdt_conduitgit.getAnyUserFromBranch(conduit, branch)
    reviewid = conduit.create_empty_revision_as_user(user)
    commenter = abdcmnt_commenter.Commenter(conduit, reviewid)
    commenter.failedCreateReview(
        branch.get_repo_name(),
        branch.review_branch_hash(),
        branch.review_branch_name(),
        branch.get_browse_url(),
        exception)
    branch.mark_new_bad_in_review(reviewid)


def try_create_review(
        mailer, conduit, branch, mail_on_fail):
    try:
        create_review(conduit, branch)
    except abdt_exception.AbdUserException as e:
        print "failed to create:"
        print e
        try:
            create_failed_review(conduit, branch, e)
        except abdt_exception.NoUsersOnBranchException as e:
            print "failed to create failed review:"
            print e
            branch.mark_bad_pre_review()
            if mail_on_fail:
                mailer.noUsersOnBranch(
                    e.review_branch_name, e.base_name, e.emails)


def process_updated_branch(mailer, conduit, branch):
    abdte = abdt_exception
    review_branch_name = branch.review_branch_name()
    if branch.is_new():
        print "create review for " + review_branch_name
        try_create_review(
            mailer,
            conduit,
            branch,
            mail_on_fail=True)
    else:
        review_id = branch.review_id_or_none()
        commenter = abdcmnt_commenter.Commenter(conduit, review_id)
        if branch.is_status_bad_pre_review():
            print "try again to create review for " + review_branch_name
            has_new_commits = branch.has_new_commits()
            try_create_review(
                mailer,
                conduit,
                branch,
                mail_on_fail=has_new_commits)
        else:
            print "update review for " + review_branch_name
            try:
                update_review(conduit, branch)
            except abdte.ReviewAbandonedException as e:
                branch.mark_bad_abandoned()
                commenter.exception(e)
            except abdte.LandingException as e:
                print "landing exception"
                branch.mark_bad_land()
                commenter.exception(e)
                conduit.set_requires_revision(review_id)
            except abdte.LandingPushBaseException as e:
                print "landing push base exception"
                # we don't need to set bad_land here, requiring revision is ok
                commenter.exception(e)
                conduit.set_requires_revision(review_id)
            except abdte.AbdUserException as e:
                print "user exception"
                branch.mark_bad_in_review()
                commenter.exception(e)


def process_abandoned_branch(conduit, branch):
    print "untracking abandoned branch: " + branch.review_branch_name()
    review_id = branch.review_id_or_none()
    if review_id is not None:
        commenter = abdcmnt_commenter.Commenter(conduit, review_id)
        commenter.abandonedBranch(branch.review_branch_name())
        # TODO: abandon the associated revision if not already
    branch.abandon()


def process_branches(branches, conduit, mailer):
    for branch in branches:
        if branch.is_abandoned():
            process_abandoned_branch(conduit, branch)
        elif branch.is_null():
            pass  # TODO: should handle these
        else:
            print "pending:", branch.review_branch_name()
            process_updated_branch(
                mailer, conduit, branch)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
