"""abd automates the creation and landing of reviews from branches."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_processrepo
#
# Public Functions:
#   isBasedOn
#   createReview
#   verifyReviewBranchBase
#   createDifferentialReview
#   updateReview
#   updateInReview
#   land
#   createFailedReview
#   tryCreateReview
#   processUpdatedBranch
#   processAbandonedBranch
#   process_branches
#
# Public Assignments:
#   MAX_DIFF_SIZE
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import abdcmnt_commenter
import abdt_conduitgit
import abdt_exception

# TODO: split into appropriate modules

_DEFAULT_TEST_PLAN = "I DIDNT TEST"
MAX_DIFF_SIZE = 1.5 * 1024 * 1024


def isBasedOn(name, base):
    # TODO: actually do this
    return True


def createReview(conduit, branch, pluginManager):
    pluginManager.hook(
        "before_create_review",
        {"conduit": conduit, "branch": branch})

    branch.verify_review_branch_base()

    # TODO: we should also cc other users on the branch
    # TODO: if there are emails that don't match up to users then we should
    #       note that on the review and perhaps use the mailer to notify them
    name, email, user = abdt_conduitgit.getPrimaryNameEmailAndUserFromBranch(
        conduit, branch)

    print "- author: " + user

    used_default_test_plan = False

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

    rawDiff = branch.make_raw_diff()

    revisionid = createDifferentialReview(
        conduit, user, parsed, branch, rawDiff)

    commenter = abdcmnt_commenter.Commenter(conduit, revisionid)

    if used_default_test_plan:
        commenter = abdcmnt_commenter.Commenter(conduit, revisionid)
        commenter.usedDefaultTestPlan(
            branch.review_branch_name(), _DEFAULT_TEST_PLAN)

    pluginManager.hook(
        "after_create_review",
        {"parsed": parsed, "conduit": conduit, "branch": branch,
            "rawDiff": rawDiff, "commenter": commenter}
    )


def verifyReviewBranchBase(gitContext, review_branch):
    if review_branch.base not in gitContext.branches:
        raise abdt_exception.MissingBaseException(
            review_branch.branch, review_branch.base)
    if not isBasedOn(review_branch.branch, review_branch.base):
        raise abdt_exception.AbdUserException(
            "'" + review_branch.branch +
            "' is not based on '" + review_branch.base + "'")


def createDifferentialReview(conduit, user, parsed, branch, rawDiff):
    print "- creating revision"
    revision_id = conduit.create_revision_as_user(rawDiff, parsed.fields, user)
    print "- created " + str(revision_id)
    branch.mark_ok_new_review(revision_id)

    print "- commenting on " + str(revision_id)
    commenter = abdcmnt_commenter.Commenter(conduit, revision_id)
    commenter.createdReview(
        branch.review_branch_name(),
        branch.base_branch_name())

    return revision_id


def updateReview(conduit, branch):
    if branch.has_new_commits():
        print "changes on branch"
        branch.verify_review_branch_base()
        updateInReview(conduit, branch)
    elif branch.is_status_bad() and not branch.is_status_bad_land():
        try:
            print "try updating bad branch"
            branch.verify_review_branch_base()
            updateInReview(conduit, branch)
        except abdt_exception.AbdUserException:
            print "still bad"

    if not branch.is_status_bad():
        if conduit.is_review_accepted(branch.review_id_or_none()):
            branch.verify_review_branch_base()
            land(conduit, branch)
            # TODO: we probably want to do a better job of cleaning up locally
        else:
            print "do nothing"


def updateInReview(conduit, branch):
    print "updateInReview"

    print "- creating diff"
    rawDiff = branch.make_raw_diff()
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
    name, email, user = abdt_conduitgit.getPrimaryNameEmailAndUserFromBranch(
        conduit, branch)

    review_id = branch.review_id_or_none()

    # compose the commit message
    message = conduit.get_commit_message(review_id)

    land_message = branch.land(name, email, message)

    print "- commenting on revision " + str(review_id)
    commenter = abdcmnt_commenter.Commenter(conduit, review_id)
    commenter.landedReview(
        branch.review_branch_name(),
        branch.base_branch_name(),
        land_message)

    conduit.close_revision(review_id)


def createFailedReview(conduit, branch, exception):
    user = abdt_conduitgit.getAnyUserFromBranch(conduit, branch)
    reviewid = conduit.create_empty_revision_as_user(user)
    commenter = abdcmnt_commenter.Commenter(conduit, reviewid)
    commenter.failedCreateReview(branch.review_branch_name(), exception)
    branch.mark_new_bad_in_review(reviewid)


def tryCreateReview(mailer, conduit, branch, pluginManager, mail_on_fail):
    try:
        createReview(conduit, branch, pluginManager)
    except abdt_exception.AbdUserException as e:
        print "failed to create:"
        print e
        try:
            createFailedReview(conduit, branch, e)
        except abdt_exception.NoUsersOnBranchException as e:
            print "failed to create failed review:"
            print e
            branch.mark_bad_pre_review()
            if mail_on_fail:
                mailer.noUsersOnBranch(
                    e.review_branch_name, e.base_name, e.emails)


def processUpdatedBranch(mailer, conduit, branch, pluginManager):
    abdte = abdt_exception
    review_branch_name = branch.review_branch_name()
    if branch.is_new():
        print "create review for " + review_branch_name
        tryCreateReview(
            mailer,
            conduit,
            branch,
            pluginManager,
            mail_on_fail=True)
    else:
        review_id = branch.review_id_or_none()
        commenter = abdcmnt_commenter.Commenter(conduit, review_id)
        if branch.is_status_bad_pre_review():
            print "try again to create review for " + review_branch_name
            has_new_commits = branch.has_new_commits()
            branch.clear_mark()
            tryCreateReview(
                mailer,
                conduit,
                branch,
                pluginManager,
                mail_on_fail=has_new_commits)
        else:
            print "update review for " + review_branch_name
            try:
                updateReview(conduit, branch)
            except abdte.LandingException as e:
                print "landing exception"
                branch.mark_bad_land()
                commenter.exception(e)
                conduit.set_requires_revision(review_id)
            except abdte.AbdUserException as e:
                print "user exception"
                branch.mark_bad_in_review()
                commenter.exception(e)


def processAbandonedBranch(conduit, branch):
    print "untracking abandoned branch: " + branch.review_branch_name()
    review_id = branch.review_id_or_none()
    if review_id is not None:
        commenter = abdcmnt_commenter.Commenter(conduit, review_id)
        commenter.abandonedBranch(branch.review_branch_name())
        # TODO: abandon the associated revision if not already
    branch.abandon()


def process_branches(branches, conduit, mailer, pluginManager):
    for branch in branches:
        if branch.is_abandoned():
            processAbandonedBranch(conduit, branch)
        elif branch.is_null():
            pass  # TODO: should handle these
        else:
            print "pending:", branch.review_branch_name()
            processUpdatedBranch(mailer, conduit, branch, pluginManager)


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
