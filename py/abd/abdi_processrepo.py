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
import abdt_branch
import abdt_conduitgit
import abdt_exception

_DEFAULT_TEST_PLAN = "I DIDNT TEST"


def create_review(conduit, branch, plugin_manager):
    plugin_manager.hook(
        "before_create_review",
        {"conduit": conduit, "branch": branch})

    branch.verify_review_branch_base()

    # TODO: we should also cc other users on the branch
    # TODO: if there are emails that don't match up to users then we should
    #       note that on the review and perhaps use the mailer to notify them
    name, email, user, phid = abdt_conduitgit.getPrimaryUserDetailsFromBranch(
        conduit, branch)

    print "- author: " + user

    used_default_test_plan = False
    removed_self_reviewer = False

    # try to get phabricator to parse the commit message and give us fields
    parsed = abdt_conduitgit.getFieldsFromBranch(conduit, branch)
    if parsed.errors:
        used_default_test_plan = True
        parsed = abdt_conduitgit.getFieldsFromBranch(
            conduit, branch, _DEFAULT_TEST_PLAN)
        if parsed.errors:
            print parsed
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
            removed_self_reviewer = True

    rawDiff = branch.make_raw_diff()

    if not rawDiff:
        raise abdt_exception.AbdUserException("no difference to review")

    revisionid = create_differential_review(
        conduit, user, parsed, branch, rawDiff)

    commenter = abdcmnt_commenter.Commenter(conduit, revisionid)

    if used_default_test_plan:
        commenter.usedDefaultTestPlan(
            branch.review_branch_name(), _DEFAULT_TEST_PLAN)

    if removed_self_reviewer:
        commenter.removedSelfReviewer(
            branch.review_branch_name(),
            branch.make_message_digest())

    plugin_manager.hook(
        "after_create_review",
        {"parsed": parsed, "conduit": conduit, "branch": branch,
            "rawDiff": rawDiff, "commenter": commenter}
    )


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
        branch.review_branch_name(),
        branch.base_branch_name(),
        branch.get_browse_url())

    return revision_id


def update_review(conduit, branch):
    if branch.has_new_commits():
        print "changes on branch"
        branch.verify_review_branch_base()
        update_in_review(conduit, branch)
    elif branch.is_status_bad() and not branch.is_status_bad_land():
        try:
            print "try updating bad branch"
            branch.verify_review_branch_base()
            update_in_review(conduit, branch)
        except abdt_exception.AbdUserException:
            print "still bad"

    if not branch.is_status_bad():
        if conduit.is_review_accepted(branch.review_id_or_none()):
            branch.verify_review_branch_base()
            land(conduit, branch)
            # TODO: we probably want to do a better job of cleaning up locally
        else:
            print "do nothing"


def update_in_review(conduit, branch):
    print "update_in_review"

    print "- creating diff"
    rawDiff = branch.make_raw_diff()

    if not rawDiff:
        raise abdt_exception.AbdUserException("no difference to review")

    review_id = branch.review_id_or_none()
    review_id_str = str(review_id)

    print "- updating revision " + review_id_str
    conduit.update_revision(review_id, rawDiff, "update")

    branch.mark_ok_in_review()

    print "- commenting on revision " + review_id_str
    commenter = abdcmnt_commenter.Commenter(conduit, review_id)
    commenter.updatedReview(branch.review_branch_name())


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

    # compose the commit message
    message = conduit.get_commit_message(review_id)

    land_message = branch.land(name, email, message)

    print "- commenting on revision " + str(review_id)
    commenter = abdcmnt_commenter.Commenter(conduit, review_id)
    commenter.landedReview(
        review_branch_name,
        base_branch_name,
        land_message)

    conduit.close_revision(review_id)


def create_failed_review(conduit, branch, exception):
    user = abdt_conduitgit.getAnyUserFromBranch(conduit, branch)
    reviewid = conduit.create_empty_revision_as_user(user)
    commenter = abdcmnt_commenter.Commenter(conduit, reviewid)
    commenter.failedCreateReview(branch.review_branch_name(), exception)
    branch.mark_new_bad_in_review(reviewid)


def try_create_review(
        mailer, conduit, branch, plugin_manager, reporter, mail_on_fail):
    try:
        create_review(conduit, branch, plugin_manager)
    except abdt_exception.AbdUserException as e:
        print "failed to create:"
        print e
        try:
            create_failed_review(conduit, branch, e)
        except abdt_exception.NoUsersOnBranchException as e:
            print "failed to create failed review:"
            print e
            branch.mark_bad_pre_review()
            reporter.no_users_on_branch(e.emails)
            if mail_on_fail:
                mailer.noUsersOnBranch(
                    e.review_branch_name, e.base_name, e.emails)


def process_updated_branch(mailer, conduit, branch, plugin_manager, reporter):
    abdte = abdt_exception
    review_branch_name = branch.review_branch_name()
    if branch.is_new():
        print "create review for " + review_branch_name
        try_create_review(
            mailer,
            conduit,
            branch,
            plugin_manager,
            reporter,
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
                plugin_manager,
                reporter,
                mail_on_fail=has_new_commits)
        else:
            print "update review for " + review_branch_name
            try:
                update_review(conduit, branch)
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


def process_branches(branches, conduit, mailer, plugin_manager, reporter):
    for branch in branches:
        if branch.is_abandoned():
            process_abandoned_branch(conduit, branch)
        elif branch.is_null():
            pass  # TODO: should handle these
        else:
            reporter.start_branch(branch.review_branch_name())
            print "pending:", branch.review_branch_name()
            process_updated_branch(
                mailer, conduit, branch, plugin_manager, reporter)
            reporter.finish_branch(
                abdt_branch.calc_is_ok(branch),
                branch.review_id_or_none())


#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#------------------------------- END-OF-FILE ----------------------------------
