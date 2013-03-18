#!/usr/bin/env python
# encoding: utf-8

"""abd automates the creation and landing of reviews from branches"""
import unittest

import abdmail_mailer
import abdmail_printsender
import abdt_exception
import abdt_naming
import phlcon_differential
import phlcon_user
import phldef_conduit
import phlgit_branch
import phlgit_checkout
import phlgit_config
import phlgit_diff
import phlgit_log
import phlgit_merge
import phlgit_push
import phlgitu_ref
import phlsys_conduit
import phlsys_fs
import phlsys_git
import phlsys_subprocess
import abdt_gittypes

#TODO: split into appropriate modules


def getPrimaryUserAndEmailFromBranch(clone, conduit, base, branch):
    hashes = phlgit_log.getRangeHashes(clone, base, branch)
    committers = phlgit_log.getCommittersFromHashes(clone, hashes)
    print "- committers: " + str(committers)
    users = phlcon_user.queryUsersFromEmails(conduit, committers)
    print "- users: " + str(users)
    primary_user = users[0]
    if not primary_user:
        raise Exception("first committer is not a Phabricator user")
    return primary_user, committers[0]


def isBasedOn(name, base):
    #TODO: actually do this
    return True


def createReview(conduit, gitContext, review_branch):
    clone = gitContext.clone
    verifyReviewBranchBase(gitContext, review_branch)

    user, email = getPrimaryUserAndEmailFromBranch(
        clone, conduit, review_branch.remote_base,
        review_branch.remote_branch)

    print "- author: " + user

    hashes = phlgit_log.getRangeHashes(
        clone, review_branch.remote_base, review_branch.remote_branch)
    parsed = getFieldsFromCommitHashes(conduit, clone, hashes)
    if parsed.errors:
        raise abdt_exception.InitialCommitMessageParseException(
            email,
            errors=parsed.errors,
            fields=parsed.fields,
            digest=makeMessageDigest(
                clone, review_branch.remote_base, review_branch.remote_branch))

    rawDiff = phlgit_diff.rawDiffRange(
        clone, review_branch.remote_base, review_branch.remote_branch)

    createDifferentialReview(
        conduit, user, parsed, gitContext, review_branch, rawDiff)


def verifyReviewBranchBase(gitContext, review_branch):
    if review_branch.base not in gitContext.branches:
        raise abdt_exception.AbdUserException(
            "base does not exist:" + review_branch.base)
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
    createMessage = ""
    createMessage += "i created this from " + review_branch.branch + ".\n"
    createMessage += " pushed to " + workingBranch + "."
    phlcon_differential.createComment(
        conduit, review.revisionid, message=createMessage, silent=True)


def makeMessageDigest(clone, base, branch):
    hashes = phlgit_log.getRangeHashes(clone, base, branch)
    revisions = phlgit_log.makeRevisionsFromHashes(clone, hashes)
    message = revisions[0].subject + "\n\n"
    for r in revisions:
        message += r.message
    return message


def updateCommitMessageFields(earlier, later):
    """Return an updated 'CommitMessageFields' based on the 'earlier' version.

    Apply the 'later' version as an update to the 'earlier' one.

    If either the earlier or later are None then the non-None one is returned.

    :earlier: a phlcon_differential.ParseCommitMessageFields
    :later: a phlcon_differential.ParseCommitMessageFields
    :returns: the updated phlcon_differential.ParseCommitMessageFields

    """
    ParseCommitMessageFields = phlcon_differential.ParseCommitMessageFields

    if earlier is None and later is not None:
        assert(isinstance(later, ParseCommitMessageFields))
        return later

    if earlier is not None and later is None:
        assert(isinstance(earlier, ParseCommitMessageFields))
        return earlier

    assert(isinstance(earlier, ParseCommitMessageFields))
    assert(isinstance(later, ParseCommitMessageFields))
    title = earlier.title
    summary = earlier.summary
    if later.summary:
        summary += "\n" + later.summary
    reviewers = set(earlier.reviewerPHIDs)
    reviewers |= set(later.reviewerPHIDs)
    reviewers = list(reviewers)
    testPlan = earlier.testPlan
    if later.testPlan:
        testPlan += "\n" + later.testPlan
    return ParseCommitMessageFields(
        title=title,
        summary=summary,
        reviewerPHIDs=reviewers,
        testPlan=testPlan)


def makeMessage(title, summary, test_plan, reviewers):
    """Return string commit message.

    :title: string title of the commit (single line)
    :summary: string summary of the commit
    :reviewers: list of string reviewers
    :test_plan: string of the test plan
    :returns: string commit message

    """
    message = ""

    extra_fields = False  # the title will have a carriage return only if True

    if summary and summary.strip():
        extra_fields = True
        message += "\n" + summary
    if test_plan and test_plan.strip():
        extra_fields = True
        message += "\n" + "Test Plan:"
        message += "\n" + test_plan
    if reviewers:
        extra_fields = True
        message += "\n" + "Reviewers:"
        message += "\n" + ' '.join(reviewers)

    if extra_fields:
        message = title + "\n" + message
    else:
        message = title

    return message


def makeMessageFromFields(conduit, fields):
    """Return a string message generated from the supplied 'fields'.

    :fields: a phlcon_differential.ParseCommitMessageFields
    :returns: a string message

    """
    user_names = phlcon_user.queryUsernamesFromPhids(
        conduit, fields.reviewerPHIDs)
    return makeMessage(
        fields.title, fields.summary, fields.testPlan, user_names)


def updateReview(conduit, gitContext, reviewBranch, workingBranch):
    rb = reviewBranch
    wb = workingBranch

    clone = gitContext.clone
    isBranchIdentical = phlgit_branch.isIdentical
    if not isBranchIdentical(clone, rb.remote_branch, wb.remote_branch):
        verifyReviewBranchBase(gitContext, reviewBranch)
        if workingBranch.status == abdt_naming.WB_STATUS_BAD_PREREVIEW:
            print "delete bad working branch"
            phlgit_push.delete(
                clone, workingBranch.branch, gitContext.remote)
            createReview(conduit, gitContext, reviewBranch)
        else:
            updateInReview(conduit, wb, gitContext, rb)
    elif not abdt_naming.isStatusBad(workingBranch):
        d = phlcon_differential
        status = d.getRevisionStatus(conduit, wb.id)
        if int(status) == d.REVISION_ACCEPTED:
            verifyReviewBranchBase(gitContext, reviewBranch)
            land(conduit, wb, gitContext, reviewBranch.branch)
            # TODO: we probably want to do a better job of cleaning up locally
        else:
            print "do nothing"


def getFieldsFromCommitHashes(conduit, clone, hashes):
    """Return a ParseCommitMessageResponse based on the commit messages.

    :conduit: supports call()
    :clone: supports call()
    :hashes: list of the commit hashes to examine
    :returns: a phlcon_differential.ParseCommitMessageResponse

    """
    d = phlcon_differential
    revisions = phlgit_log.makeRevisionsFromHashes(clone, hashes)
    fields = None
    for r in revisions:
        p = d.parseCommitMessage(
            conduit, r.subject + "\n\n" + r.message)
        f = phlcon_differential.ParseCommitMessageFields(**p.fields)
        fields = updateCommitMessageFields(fields, f)
    message = makeMessageFromFields(conduit, fields)
    return d.parseCommitMessage(conduit, message)


def updateInReview(conduit, wb, gitContext, review_branch):
    remoteBranch = review_branch.remote_branch
    clone = gitContext.clone
    user, email = getPrimaryUserAndEmailFromBranch(
        clone, conduit, wb.remote_base, remoteBranch)

    print "updateInReview"

    print "- creating diff"
    rawDiff = phlgit_diff.rawDiffRange(clone, wb.remote_base, remoteBranch)

    d = phlcon_differential
    with phlsys_conduit.actAsUserContext(conduit, user):
        diffid = d.createRawDiff(conduit, rawDiff).id

        print "- updating revision " + str(wb.id)
        hashes = phlgit_log.getRangeHashes(clone, wb.remote_base, remoteBranch)
        parsed = getFieldsFromCommitHashes(conduit, clone, hashes)
        if parsed.errors:
            raise abdt_exception.CommitMessageParseException(
                errors=parsed.errors,
                fields=parsed.fields,
                digest=makeMessageDigest(clone, wb.remote_base, remoteBranch))

        d.updateRevision(
            conduit, wb.id, diffid, parsed.fields, "update")

    pushWorkingBranchStatus(
        gitContext,
        review_branch,
        wb,
        abdt_naming.WB_STATUS_OK)

    print "- commenting on revision " + str(wb.id)
    updateMessage = ""
    updateMessage += "i updated this from " + wb.branch + ".\n"
    updateMessage += "pushed to " + wb.branch + "."
    d.createComment(
        conduit, wb.id, message=updateMessage, silent=True)


def land(conduit, wb, gitContext, branch):
    clone = gitContext.clone
    print "landing " + wb.remote_branch + " onto " + wb.remote_base
    user, email = getPrimaryUserAndEmailFromBranch(
        clone, conduit, wb.remote_base, wb.remote_branch)
    d = phlcon_differential
    with phlsys_conduit.actAsUserContext(conduit, user):
        phlgit_checkout.newBranchForceBasedOn(clone, wb.base, wb.remote_base)

        # compose the commit message
        info = d.query(conduit, [wb.id])[0]
        userNames = phlcon_user.queryUsernamesFromPhids(
            conduit, info.reviewers)
        message = makeMessage(
            info.title, info.summary, info.testPlan, userNames)
        message += "\nDifferential Revision: " + info.uri

        squashMessage = phlgit_merge.squash(
            clone, wb.remote_branch, message)
        print "- pushing " + wb.remote_base
        phlgit_push.push(clone, wb.base, gitContext.remote)
        print "- deleting " + wb.branch
        phlgit_push.delete(clone, wb.branch, gitContext.remote)
        print "- deleting " + branch
        phlgit_push.delete(clone, branch, gitContext.remote)

    print "- commenting on revision " + str(wb.id)
    closeMessage = ""
    closeMessage += "i landed this on " + wb.base + ".\n"
    closeMessage += "deleted " + wb.branch + "\n"
    closeMessage += "deleted " + branch + "."
    d.createComment(
        conduit, wb.id, message=closeMessage, silent=True)
    d.createComment(
        conduit, wb.id, message=squashMessage, silent=True)

    with phlsys_conduit.actAsUserContext(conduit, user):
        d.close(conduit, wb.id)
    # TODO: we probably want to do a better job of cleaning up locally


def pushBadPreReviewWorkingBranch(gitContext, review_branch):
    working_branch_name = abdt_naming.makeWorkingBranchName(
        abdt_naming.WB_STATUS_BAD_PREREVIEW,
        review_branch.description, review_branch.base, "none")
    phlgit_push.pushAsymmetrical(
        gitContext.clone,
        phlgitu_ref.makeRemote(
            review_branch.branch, gitContext.remote),
        phlgitu_ref.makeLocal(working_branch_name),
        gitContext.remote)


def pushWorkingBranchStatus(
        gitContext, review_branch, working_branch, status):
    clone = gitContext.clone
    remote = gitContext.remote
    old_branch = working_branch.branch

    working_branch = abdt_gittypes.makeWorkingBranchWithStatus(
        working_branch, status)

    new_branch = working_branch.branch
    if old_branch == new_branch:
        phlgit_push.pushAsymmetricalForce(
            clone,
            review_branch.remote_branch,
            phlgitu_ref.makeLocal(new_branch),
            remote)
    else:
        phlgit_push.moveAsymmetrical(
            clone,
            review_branch.remote_branch,
            phlgitu_ref.makeLocal(old_branch),
            phlgitu_ref.makeLocal(new_branch),
            remote)


def pushBadInReviewWorkingBranch(gitContext, review_branch, working_branch):
    pushWorkingBranchStatus(
        gitContext,
        review_branch,
        working_branch,
        abdt_naming.WB_STATUS_BAD_INREVIEW)


def processUpdatedRepo(conduit, path, remote):
    print_sender = abdmail_printsender.MailSender("phab@server.test")
    mailer = abdmail_mailer.Mailer(
        print_sender,
        ["admin@server.test"],
        "http://server.fake/testrepo.git")
    with phlsys_fs.chDirContext(path):
        clone = phlsys_git.GitClone(".")
        remote_branches = phlgit_branch.getRemote(clone, remote)
        gitContext = abdt_gittypes.GitContext(clone, remote, remote_branches)
        wbList = abdt_naming.getWorkingBranches(remote_branches)
        makeRb = abdt_naming.makeReviewBranchNameFromWorkingBranch
        rbDict = dict((makeRb(wb), wb) for wb in wbList)
        for b in remote_branches:
            if abdt_naming.isReviewBranchName(b):
                review_branch = abdt_naming.makeReviewBranchFromName(b)
                review_branch = abdt_gittypes.makeGitReviewBranch(
                    review_branch, remote)
                abdte = abdt_exception
                if b not in rbDict.keys():
                    print "create review for " + b
                    try:
                        createReview(
                            conduit, gitContext, review_branch)
                    except abdte.InitialCommitMessageParseException as e:
                        pushBadPreReviewWorkingBranch(
                            gitContext, review_branch)
                        mailer.badBranchName(e.email, review_branch)
                else:
                    print "update review for " + b
                    working_branch = rbDict[b]
                    working_branch = abdt_gittypes.makeGitWorkingBranch(
                        working_branch, remote)
                    try:
                        updateReview(
                            conduit, gitContext,
                            review_branch, working_branch)
                    except abdte.InitialCommitMessageParseException as e:
                        pushBadPreReviewWorkingBranch(
                            gitContext, review_branch)
                        mailer.badBranchName(e.email, review_branch)
                    except abdte.CommitMessageParseException as e:
                        pushBadInReviewWorkingBranch(
                            gitContext, review_branch, working_branch)
                        # TODO: update the review with a message


def runCommands(*commands):
    phlsys_subprocess.runCommands(*commands)


# TODO: break this down
class TestAbd(unittest.TestCase):

    def _gitCommitAll(self, subject, testPlan, reviewer):
        reviewers = [reviewer] if reviewer else None
        message = makeMessage(subject, None, testPlan, reviewers)
        phlsys_subprocess.run("git", "commit", "-a", "-F", "-", stdin=message)

    def _createCommitNewFileRaw(self, filename, testPlan=None, reviewer=None):
        runCommands("touch " + filename)
        runCommands("git add " + filename)
        self._gitCommitAll("add " + filename, testPlan, reviewer)

    def _createCommitNewFile(self, filename, reviewer):
        runCommands("touch " + filename)
        runCommands("git add " + filename)
        self._gitCommitAll("add " + filename, "test plan", reviewer)

    def setUp(self):
        self.reviewer = phldef_conduit.alice.user
        #TODO: just make a temp dir
        runCommands("rm -rf abd-test")
        runCommands("mkdir abd-test")
        with phlsys_fs.chDirContext("abd-test"):
            runCommands(
                "git --git-dir=devgit init --bare",
                "git clone devgit developer",
                "git clone devgit phab",
            )

            devClone = phlsys_git.GitClone("developer")
            phlgit_config.setUsernameEmail(
                devClone,
                phldef_conduit.bob.user,
                phldef_conduit.bob.email)

            with phlsys_fs.chDirContext("developer"):
                self._createCommitNewFile("README", self.reviewer)

                runCommands("git push origin master")

            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")

    def _countPhabWorkingBranches(self):
        with phlsys_fs.chDirContext("phab"):
            clone = phlsys_git.GitClone(".")
            branches = phlgit_branch.getRemote(clone, "origin")
        wbList = abdt_naming.getWorkingBranches(branches)
        return len(wbList)

    def _countPhabBadWorkingBranches(self):
        with phlsys_fs.chDirContext("phab"):
            clone = phlsys_git.GitClone(".")
            branches = phlgit_branch.getRemote(clone, "origin")
        wbList = abdt_naming.getWorkingBranches(branches)
        numBadBranches = 0
        for wb in wbList:
            if abdt_naming.isStatusBad(wb):
                numBadBranches += 1
        return numBadBranches

    def test_nothingToDo(self):
        with phlsys_fs.chDirContext("abd-test"):
            conduit = phlsys_conduit.Conduit(
                phldef_conduit.test_uri,
                phldef_conduit.phab.user,
                phldef_conduit.phab.certificate)

            # nothing to process
            processUpdatedRepo(conduit, "phab", "origin")

    def test_simpleWorkflow(self):
        with phlsys_fs.chDirContext("abd-test"):
            conduit = phlsys_conduit.Conduit(
                phldef_conduit.test_uri,
                phldef_conduit.phab.user,
                phldef_conduit.phab.certificate)

            # nothing to process
            processUpdatedRepo(conduit, "phab", "origin")

            with phlsys_fs.chDirContext("developer"):
                runCommands("git checkout -b ph-review/change/master")
                self._createCommitNewFile("NEWFILE", self.reviewer)

                runCommands("git push -u origin ph-review/change/master")

            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")

            # create the review
            processUpdatedRepo(conduit, "phab", "origin")

            # update the review with a new revision
            with phlsys_fs.chDirContext("developer"):
                self._createCommitNewFileRaw("NEWFILE2")
                runCommands("git push -u origin ph-review/change/master")
            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")

            # update the review
            processUpdatedRepo(conduit, "phab", "origin")

            # accept the review
            with phlsys_fs.chDirContext("phab"):
                clone = phlsys_git.GitClone(".")
                branches = phlgit_branch.getRemote(clone, "origin")
            wbList = abdt_naming.getWorkingBranches(branches)
            self.assertEqual(len(wbList), 1)
            wb = wbList[0]
            with phlsys_conduit.actAsUserContext(conduit, self.reviewer):
                phlcon_differential.createComment(
                    conduit, wb.id, action="accept")

            processUpdatedRepo(conduit, "phab", "origin")
            self.assertEqual(self._countPhabWorkingBranches(), 0)

    def test_badMsgWorkflow(self):
        with phlsys_fs.chDirContext("abd-test"):
            conduit = phlsys_conduit.Conduit(
                phldef_conduit.test_uri,
                phldef_conduit.phab.user,
                phldef_conduit.phab.certificate)

            # nothing to process
            processUpdatedRepo(conduit, "phab", "origin")

            with phlsys_fs.chDirContext("developer"):
                runCommands("git checkout -b ph-review/change/master")
                self._createCommitNewFileRaw(
                    "NEWFILE", reviewer=self.reviewer)
                runCommands("git push -u origin ph-review/change/master")

            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")

            # fail to create the review
            processUpdatedRepo(conduit, "phab", "origin")
            self.assertEqual(self._countPhabWorkingBranches(), 1)
            self.assertEqual(self._countPhabBadWorkingBranches(), 1)

            # make a new commit with another bad message
            with phlsys_fs.chDirContext("developer"):
                self._createCommitNewFileRaw("NEWFILE2")
                runCommands("git push -u origin ph-review/change/master")

            # fail to create the review again
            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")
            processUpdatedRepo(conduit, "phab", "origin")
            self.assertEqual(self._countPhabWorkingBranches(), 1)
            self.assertEqual(self._countPhabBadWorkingBranches(), 1)

            # make a new commit with good message
            with phlsys_fs.chDirContext("developer"):
                self._createCommitNewFileRaw(
                    "NEWFILE3", testPlan="test plan")
                runCommands("git push -u origin ph-review/change/master")

            # create the review ok
            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")
            processUpdatedRepo(conduit, "phab", "origin")
            self.assertEqual(self._countPhabWorkingBranches(), 1)
            self.assertEqual(self._countPhabBadWorkingBranches(), 0)

            # rewrite history with a bad message
            with phlsys_fs.chDirContext("developer"):
                runCommands("git reset origin/master --hard")
                self._createCommitNewFileRaw(
                    "NEWFILE", reviewer=self.reviewer)
                runCommands(
                    "git push -u origin ph-review/change/master --force")

            # fail to update the review
            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")
            processUpdatedRepo(conduit, "phab", "origin")
            self.assertEqual(self._countPhabWorkingBranches(), 1)
            self.assertEqual(self._countPhabBadWorkingBranches(), 1)

            # make a new commit with good message
            with phlsys_fs.chDirContext("developer"):
                self._createCommitNewFileRaw(
                    "NEWFILE2", testPlan="test plan")
                runCommands("git push -u origin ph-review/change/master")

            # update the review ok
            print
            print "update the review ok"
            print "--------------------"
            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")
            processUpdatedRepo(conduit, "phab", "origin")
            self.assertEqual(self._countPhabWorkingBranches(), 1)
            self.assertEqual(self._countPhabBadWorkingBranches(), 0)
            print

            # accept the review
            with phlsys_fs.chDirContext("phab"):
                clone = phlsys_git.GitClone(".")
                branches = phlgit_branch.getRemote(clone, "origin")
            wbList = abdt_naming.getWorkingBranches(branches)
            self.assertEqual(len(wbList), 1)
            wb = wbList[0]
            with phlsys_conduit.actAsUserContext(conduit, self.reviewer):
                phlcon_differential.createComment(
                    conduit, wb.id, action="accept")

            # land the revision
            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")
            processUpdatedRepo(conduit, "phab", "origin")
            self.assertEqual(self._countPhabWorkingBranches(), 0)

    def test_badBaseWorkflow(self):
        with phlsys_fs.chDirContext("abd-test"):
            conduit = phlsys_conduit.Conduit(
                phldef_conduit.test_uri,
                phldef_conduit.phab.user,
                phldef_conduit.phab.certificate)

            with phlsys_fs.chDirContext("developer"):
                runCommands("git checkout -b ph-review/change/blaster")
                self._createCommitNewFile("NEWFILE", self.reviewer)
                runCommands("git push -u origin ph-review/change/blaster")

            with phlsys_fs.chDirContext("phab"):
                runCommands("git fetch origin -p")

            # fail to create the review
            #processUpdatedRepo(conduit, "phab", "origin")
            self.assertRaises(
                abdt_exception.AbdUserException,
                processUpdatedRepo, conduit, "phab", "origin")

            #self.assertEqual(self.countPhabBadWorkingBranches(), 1)

    def tearDown(self):
        runCommands("rm -rf abd-test")
        pass


if __name__ == "__main__":
    unittest.main()

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
