#!/usr/bin/env python
# encoding: utf-8

"""abd automates the creation and landing of reviews from branches"""
import subprocess

# XXX: probably too many imports
import abdcmnt_commenter
import abdt_exception
import abdt_naming
import phlcon_differential
import phlcon_user
import phlgit_branch
import phlgit_checkout
import phlgit_diff
import phlgit_log
import phlgit_merge
import phlgit_push
import phlsys_conduit
import phlsys_fs
import phlsys_git
import abdt_gittypes
import abdt_conduit
import abdt_conduitgit
import abdt_workingbranch

#TODO: split into appropriate modules

_DEFAULT_TEST_PLAN = "I DIDNT TEST"


def isBasedOn(name, base):
    #TODO: actually do this
    return True


def createReview(conduit, gitContext, review_branch):
    clone = gitContext.clone
    verifyReviewBranchBase(gitContext, review_branch)

    # TODO: we should also cc other users on the branch
    # TODO: if there are emails that don't match up to users then we should
    #       note that on the review and perhaps use the mailer to notify them
    name, email, user = abdt_conduitgit.getPrimaryNameEmailAndUserFromBranch(
        clone, conduit, review_branch.remote_base,
        review_branch.remote_branch)

    print "- author: " + user

    used_default_test_plan = False

    hashes = phlgit_log.getRangeHashes(
        clone, review_branch.remote_base, review_branch.remote_branch)
    commit = hashes[-1]
    parsed = abdt_conduitgit.getFieldsFromCommitHash(
        conduit, clone, commit)
    if parsed.errors:
        used_default_test_plan = True
        parsed = abdt_conduitgit.getFieldsFromCommitHash(
            conduit, clone, commit, _DEFAULT_TEST_PLAN)
        if parsed.errors:
            print parsed
            raise abdt_exception.CommitMessageParseException(
                errors=parsed.errors,
                fields=parsed.fields,
                digest=makeMessageDigest(
                    clone,
                    review_branch.remote_base,
                    review_branch.remote_branch))

    rawDiff = phlgit_diff.rawDiffRange(
        clone, review_branch.remote_base, review_branch.remote_branch, 1000)

    revisionid = createDifferentialReview(
        conduit, user, parsed, gitContext, review_branch, rawDiff)

    if used_default_test_plan:
        commenter = abdcmnt_commenter.Commenter(conduit, revisionid)
        commenter.usedDefaultTestPlan(review_branch.branch, _DEFAULT_TEST_PLAN)


def verifyReviewBranchBase(gitContext, review_branch):
    if review_branch.base not in gitContext.branches:
        raise abdt_exception.MissingBaseException(
            review_branch.branch, review_branch.base)
    if not isBasedOn(review_branch.branch, review_branch.base):
        raise abdt_exception.AbdUserException(
            "'" + review_branch.branch +
            "' is not based on '" + review_branch.base + "'")


def createDifferentialReview(
        conduit, user, parsed, gitContext, review_branch, rawDiff):
    clone = gitContext.clone
    phlgit_checkout.newBranchForceBasedOn(
        clone, review_branch.branch, review_branch.remote_branch)

    with phlsys_conduit.actAsUserContext(conduit, user):
        print "- creating diff"
        diffid = phlcon_differential.createRawDiff(conduit, rawDiff).id

        print "- creating revision"
        review = phlcon_differential.createRevision(
            conduit, diffid, parsed.fields)
        print "- created " + str(review.revisionid)

        workingBranch = abdt_naming.makeWorkingBranchName(
            abdt_naming.WB_STATUS_OK,
            review_branch.description,
            review_branch.base,
            review.revisionid)

        print "- pushing working branch: " + workingBranch
        phlgit_push.pushAsymmetrical(
            clone, review_branch.branch, workingBranch, gitContext.remote)

    print "- commenting on " + str(review.revisionid)
    commenter = abdcmnt_commenter.Commenter(conduit, review.revisionid)
    commenter.createdReview(review_branch.branch, review_branch.base)

    return review.revisionid


def makeMessageDigest(clone, base, branch):
    hashes = phlgit_log.getRangeHashes(clone, base, branch)
    revisions = phlgit_log.makeRevisionsFromHashes(clone, hashes)
    message = revisions[0].subject + "\n\n"
    for r in revisions:
        message += r.message
    return message


def updateReview(conduit, gitContext, reviewBranch, workingBranch, author):
    rb = reviewBranch
    wb = workingBranch

    clone = gitContext.clone
    isBranchIdentical = phlgit_branch.isIdentical
    if not isBranchIdentical(clone, rb.remote_branch, wb.remote_branch):
        print "changes on branch"
        verifyReviewBranchBase(gitContext, reviewBranch)
        wb = updateInReview(conduit, wb, gitContext, rb, author)
    elif abdt_naming.isStatusBad(wb) and not abdt_naming.isStatusBadLand(wb):
        d = phlcon_differential
        status = d.getRevisionStatus(conduit, wb.id)
        try:
            print "try updating bad branch"
            verifyReviewBranchBase(gitContext, reviewBranch)
            updateInReview(conduit, wb, gitContext, rb, author)
        except abdt_exception.AbdUserException:
            print "still bad"

    if not abdt_naming.isStatusBad(wb):
        d = phlcon_differential
        status = d.getRevisionStatus(conduit, wb.id)
        if int(status) == d.REVISION_ACCEPTED:
            verifyReviewBranchBase(gitContext, reviewBranch)
            land(conduit, wb, gitContext, reviewBranch.branch)
            # TODO: we probably want to do a better job of cleaning up locally
        else:
            print "do nothing"


def updateInReview(conduit, wb, gitContext, review_branch, author):
    remoteBranch = review_branch.remote_branch
    clone = gitContext.clone

    print "updateInReview"

    print "- creating diff"
    rawDiff = phlgit_diff.rawDiffRange(
        clone, wb.remote_base, remoteBranch, 1000)
    if not rawDiff:
        raise abdt_exception.AbdUserException(
            "no difference from " + wb.base + " to " + wb.branch)

    d = phlcon_differential
    used_default_test_plan = False
    with phlsys_conduit.actAsUserContext(conduit, author):
        print "- updating revision " + str(wb.id)
        diffid = d.createRawDiff(conduit, rawDiff).id
        d.updateRevision(
            conduit, wb.id, diffid, [], "update")

    wb = abdt_workingbranch.pushStatus(
        gitContext,
        review_branch,
        wb,
        abdt_naming.WB_STATUS_OK)

    print "- commenting on revision " + str(wb.id)
    commenter = abdcmnt_commenter.Commenter(conduit, wb.id)
    commenter.updatedReview(review_branch.branch)
    if used_default_test_plan:
        commenter.usedDefaultTestPlan(wb.branch, _DEFAULT_TEST_PLAN)

    return wb


def land(conduit, wb, gitContext, branch):
    clone = gitContext.clone
    print "landing " + wb.remote_branch + " onto " + wb.remote_base
    name, email, user = abdt_conduitgit.getPrimaryNameEmailAndUserFromBranch(
        clone, conduit, wb.remote_base, wb.remote_branch)
    d = phlcon_differential
    with phlsys_conduit.actAsUserContext(conduit, user):
        phlgit_checkout.newBranchForceBasedOn(clone, wb.base, wb.remote_base)

        # compose the commit message
        message = d.getCommitMessage(conduit, wb.id)

        try:
            with phlsys_fs.nostd():
                squashMessage = phlgit_merge.squash(
                    clone,
                    wb.remote_branch,
                    message,
                    name + " <" + email + ">")
        except subprocess.CalledProcessError as e:
            clone.call("reset", "--hard")  # fix the working copy
            raise abdt_exception.LandingException(str(e) + "\n" + e.output)

        print "- pushing " + wb.remote_base
        phlgit_push.push(clone, wb.base, gitContext.remote)
        print "- deleting " + wb.branch
        phlgit_push.delete(clone, wb.branch, gitContext.remote)
        print "- deleting " + branch
        phlgit_push.delete(clone, branch, gitContext.remote)

    print "- commenting on revision " + str(wb.id)
    commenter = abdcmnt_commenter.Commenter(conduit, wb.id)
    commenter.landedReview(branch, wb.base, squashMessage)

    authorPHID = d.query(conduit, [wb.id])[0].authorPHID
    authorUser = phlcon_user.queryUsernamesFromPhids(conduit, [authorPHID])[0]
    # TODO: there's a potential race condition on the author here
    with phlsys_conduit.actAsUserContext(conduit, authorUser):
        d.close(conduit, wb.id)
    # TODO: we probably want to do a better job of cleaning up locally


def createFailedReview(conduit, gitContext, review_branch, exception):
    user = abdt_conduitgit.getAnyUserFromBranch(
        gitContext.clone,
        conduit,
        review_branch.remote_base,
        review_branch.remote_branch)
    reviewid = abdt_conduit.createEmptyRevision(conduit, user)
    wb = abdt_gittypes.makeGitWorkingBranchFromParts(
        abdt_naming.WB_STATUS_BAD_INREVIEW,
        review_branch.description,
        review_branch.base,
        reviewid,
        gitContext.remote)
    commenter = abdcmnt_commenter.Commenter(
        conduit, reviewid)
    commenter.failedCreateReview(review_branch.branch, exception)
    abdt_workingbranch.pushBadInReview(
        gitContext, review_branch, wb)


def tryCreateReview(mailer, conduit, gitContext, review_branch, mail_on_fail):
    try:
        createReview(conduit, gitContext, review_branch)
    except abdt_exception.AbdUserException as e:
        try:
            createFailedReview(conduit, gitContext, review_branch, e)
        except abdt_exception.NoUsersOnBranchException as e:
            abdt_workingbranch.pushBadPreReview(
                gitContext, review_branch)
            if mail_on_fail:
                mailer.noUsersOnBranch(
                    e.review_branch_name, e.base_name, e.emails)


def processUpdatedBranch(
        mailer, conduit, gitContext, review_branch, working_branch):
    abdte = abdt_exception
    if working_branch is None:
        print "create review for " + review_branch.branch
        tryCreateReview(
            mailer, conduit, gitContext, review_branch, mail_on_fail=True)
    else:
        commenter = abdcmnt_commenter.Commenter(conduit, working_branch.id)
        if abdt_naming.isStatusBadPreReview(working_branch):
            hasChanged = not phlgit_branch.isIdentical(
                gitContext.clone,
                review_branch.remote_branch,
                working_branch.remote_branch)
            print "try again to create review for " + review_branch.branch
            phlgit_push.delete(
                gitContext.clone,
                working_branch.branch,
                gitContext.remote)
            tryCreateReview(
                mailer,
                conduit,
                gitContext,
                review_branch,
                mail_on_fail=hasChanged)
        else:
            print "update review for " + review_branch.branch
            revision = phlcon_differential.query(
                conduit, [working_branch.id])[0]
            author_user = phlcon_user.queryUsernamesFromPhids(
                conduit, [revision.authorPHID])[0]
            try:
                updateReview(
                    conduit,
                    gitContext,
                    review_branch,
                    working_branch,
                    author_user)
            except abdte.LandingException as e:
                print "landing exception"
                abdt_workingbranch.pushBadLand(
                    gitContext, review_branch, working_branch)
                commenter.exception(e)
                with phlsys_conduit.actAsUserContext(conduit, author_user):
                    phlcon_differential.createComment(
                        conduit,
                        working_branch.id,
                        action=phlcon_differential.ACTION_RETHINK)
            except abdte.AbdUserException as e:
                print "user exception"
                abdt_workingbranch.pushBadInReview(
                    gitContext, review_branch, working_branch)
                commenter.exception(e)


def processAbandonedBranches(conduit, clone, remote, wbList, remote_branches):
    for wb in wbList:
        rb = abdt_naming.makeReviewBranchNameFromWorkingBranch(wb)
        if rb not in remote_branches:
            print "delete abandoned branch: " + wb.branch
            try:
                revisionid = int(wb.id)
            except ValueError:
                pass
            else:
                commenter = abdcmnt_commenter.Commenter(conduit, revisionid)
                commenter.abandonedBranch(rb)
                # TODO: abandon the associated revision if not already
            phlgit_push.delete(clone, wb.branch, remote)


def processUpdatedRepo(conduit, path, remote, mailer):
    clone = phlsys_git.GitClone(path)
    remote_branches = phlgit_branch.getRemote(clone, remote)
    gitContext = abdt_gittypes.GitContext(clone, remote, remote_branches)
    wbList = abdt_naming.getWorkingBranches(remote_branches)
    makeRb = abdt_naming.makeReviewBranchNameFromWorkingBranch
    rbDict = dict((makeRb(wb), wb) for wb in wbList)

    processAbandonedBranches(conduit, clone, remote, wbList, remote_branches)

    for b in remote_branches:
        if abdt_naming.isReviewBranchPrefixed(b):
            review_branch = abdt_naming.makeReviewBranchFromName(b)
            if review_branch is None:
                # TODO: handle this case properly
                continue

            review_branch = abdt_gittypes.makeGitReviewBranch(
                review_branch, remote)
            working_branch = None
            if b in rbDict.keys():
                working_branch = rbDict[b]
                working_branch = abdt_gittypes.makeGitWorkingBranch(
                    working_branch, remote)
            processUpdatedBranch(
                mailer, conduit, gitContext, review_branch, working_branch)


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
