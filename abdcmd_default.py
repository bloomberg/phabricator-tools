#!/usr/bin/env python
# encoding: utf-8

"""abd automates the creation and landing of reviews from branches"""
import os
import unittest

import abdmail_mailer
import abdmail_printsender
import abdcmnt_commenter
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
import phlsys_conduit
import phlsys_fs
import phlsys_git
import phlsys_subprocess
import abdt_gittypes
import abdt_commitmessage
import abdt_conduitgit
import abdt_workingbranch


#TODO: split into appropriate modules


def isBasedOn(name, base):
    #TODO: actually do this
    return True


def createReview(conduit, gitContext, review_branch):
    clone = gitContext.clone
    verifyReviewBranchBase(gitContext, review_branch)

    user, email = abdt_conduitgit.getPrimaryUserAndEmailFromBranch(
        clone, conduit, review_branch.remote_base,
        review_branch.remote_branch)

    print "- author: " + user

    hashes = phlgit_log.getRangeHashes(
        clone, review_branch.remote_base, review_branch.remote_branch)
    parsed = abdt_conduitgit.getFieldsFromCommitHashes(conduit, clone, hashes)
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


def updateReview(conduit, gitContext, reviewBranch, workingBranch):
    rb = reviewBranch
    wb = workingBranch

    clone = gitContext.clone
    isBranchIdentical = phlgit_branch.isIdentical
    if not isBranchIdentical(clone, rb.remote_branch, wb.remote_branch):
        verifyReviewBranchBase(gitContext, reviewBranch)
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


def updateInReview(conduit, wb, gitContext, review_branch):
    remoteBranch = review_branch.remote_branch
    clone = gitContext.clone
    user, email = abdt_conduitgit.getPrimaryUserAndEmailFromBranch(
        clone, conduit, wb.remote_base, remoteBranch)

    print "updateInReview"

    print "- creating diff"
    rawDiff = phlgit_diff.rawDiffRange(clone, wb.remote_base, remoteBranch)

    d = phlcon_differential
    with phlsys_conduit.actAsUserContext(conduit, user):
        diffid = d.createRawDiff(conduit, rawDiff).id

        print "- updating revision " + str(wb.id)
        hashes = phlgit_log.getRangeHashes(clone, wb.remote_base, remoteBranch)
        parsed = abdt_conduitgit.getFieldsFromCommitHashes(
            conduit, clone, hashes)
        if parsed.errors:
            raise abdt_exception.CommitMessageParseException(
                errors=parsed.errors,
                fields=parsed.fields,
                digest=makeMessageDigest(clone, wb.remote_base, remoteBranch))

        d.updateRevision(
            conduit, wb.id, diffid, parsed.fields, "update")

    abdt_workingbranch.pushStatus(
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
    user, email = abdt_conduitgit.getPrimaryUserAndEmailFromBranch(
        clone, conduit, wb.remote_base, wb.remote_branch)
    d = phlcon_differential
    with phlsys_conduit.actAsUserContext(conduit, user):
        phlgit_checkout.newBranchForceBasedOn(clone, wb.base, wb.remote_base)

        # compose the commit message
        info = d.query(conduit, [wb.id])[0]
        userNames = phlcon_user.queryUsernamesFromPhids(
            conduit, info.reviewers)
        message = abdt_commitmessage.make(
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


def processUpdatedBranch(
        mailer, conduit, gitContext, review_branch, working_branch):
    abdte = abdt_exception
    if working_branch is None:
        print "create review for " + review_branch.branch
        try:
            createReview(conduit, gitContext, review_branch)
        except abdte.InitialCommitMessageParseException as e:
            abdt_workingbranch.pushBadPreReview(gitContext, review_branch)
            mailer.initialCommitMessageParseException(e, review_branch.branch)
        except abdte.AbdUserException as e:
            abdt_workingbranch.pushBadPreReview(gitContext, review_branch)
            mailer.userException(e.message, review_branch.branch)
    else:
        commenter = abdcmnt_commenter.Commenter(conduit, working_branch.id)
        if abdt_naming.isStatusBadPreReview(working_branch):
            print "try again to create review for " + review_branch.branch
            try:
                phlgit_push.delete(
                    gitContext.clone,
                    working_branch.branch,
                    gitContext.remote)
                createReview(conduit, gitContext, review_branch)
            except abdte.InitialCommitMessageParseException as e:
                abdt_workingbranch.pushBadPreReview(gitContext, review_branch)
                mailer.initialCommitMessageParseException(
                    e, review_branch.branch)
            except abdte.AbdUserException as e:
                abdt_workingbranch.pushBadPreReview(gitContext, review_branch)
                mailer.userException(e.message, review_branch.branch)
        else:
            print "update review for " + review_branch.branch
            try:
                updateReview(
                    conduit,
                    gitContext,
                    review_branch,
                    working_branch)
            except abdte.InitialCommitMessageParseException as e:
                raise e
            except abdte.CommitMessageParseException as e:
                abdt_workingbranch.pushBadInReview(
                    gitContext, review_branch, working_branch)
                commenter.commitMessageParseException(e)


def processUpdatedRepo(conduit, path, remote):
    print_sender = abdmail_printsender.MailSender("phab@server.test")
    mailer = abdmail_mailer.Mailer(
        print_sender,
        ["admin@server.test"],
        "http://server.fake/testrepo.git")
    clone = phlsys_git.GitClone(path)
    remote_branches = phlgit_branch.getRemote(clone, remote)
    gitContext = abdt_gittypes.GitContext(clone, remote, remote_branches)
    wbList = abdt_naming.getWorkingBranches(remote_branches)
    makeRb = abdt_naming.makeReviewBranchNameFromWorkingBranch
    rbDict = dict((makeRb(wb), wb) for wb in wbList)
    for wb in wbList:
        rb = makeRb(wb)
        if rb not in remote_branches:
            print "delete orphaned branch: " + wb.branch
            phlgit_push.delete(clone, wb.branch, remote)
            # TODO: update the associated revision if there is one
    for b in remote_branches:
        if abdt_naming.isReviewBranchName(b):
            review_branch = abdt_naming.makeReviewBranchFromName(b)
            review_branch = abdt_gittypes.makeGitReviewBranch(
                review_branch, remote)
            working_branch = None
            if b in rbDict.keys():
                working_branch = rbDict[b]
                working_branch = abdt_gittypes.makeGitWorkingBranch(
                    working_branch, remote)
            processUpdatedBranch(
                mailer, conduit, gitContext, review_branch, working_branch)


def runCommands(*commands):
    phlsys_subprocess.runCommands(*commands)


# TODO: break this down
class TestAbd(unittest.TestCase):

    def _gitCommitAll(self, subject, testPlan, reviewer):
        reviewers = [reviewer] if reviewer else None
        message = abdt_commitmessage.make(subject, None, testPlan, reviewers)
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
        self.author_account = phldef_conduit.bob
        #TODO: just make a temp dir
        runCommands("rm -rf abd-test")
        runCommands("mkdir abd-test")
        self._saved_path = os.getcwd()
        os.chdir("abd-test")
        runCommands(
            "git --git-dir=devgit init --bare",
            "git clone devgit developer",
            "git clone devgit phab",
        )

        self._devSetAuthorAccount(self.author_account)

        with phlsys_fs.chDirContext("developer"):
            self._createCommitNewFile("README", self.reviewer)
            runCommands("git push origin master")

        with phlsys_fs.chDirContext("phab"):
            runCommands("git fetch origin -p")

        self.conduit = phlsys_conduit.Conduit(
            phldef_conduit.test_uri,
            phldef_conduit.phab.user,
            phldef_conduit.phab.certificate)

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

    def _phabUpdate(self):
        with phlsys_fs.chDirContext("phab"):
            runCommands("git fetch origin -p")
        processUpdatedRepo(self.conduit, "phab", "origin")

    def _phabUpdateWithExpectations(self, total=None, bad=None):
        with phlsys_fs.chDirContext("phab"):
            runCommands("git fetch origin -p")
        processUpdatedRepo(self.conduit, "phab", "origin")
        if total is not None:
            self.assertEqual(self._countPhabWorkingBranches(), total)
        if bad is not None:
            self.assertEqual(self._countPhabBadWorkingBranches(), bad)

    def _devSetAuthorAccount(self, account):
        devClone = phlsys_git.GitClone("developer")
        phlgit_config.setUsernameEmail(devClone, account.user, account.email)

    def _devResetBranchToMaster(self, branch):
        with phlsys_fs.chDirContext("developer"):
            runCommands("git reset origin/master --hard")
            runCommands("git push -u origin " + branch + " --force")

    def _devCheckoutPushNewBranch(self, branch):
        with phlsys_fs.chDirContext("developer"):
            runCommands("git checkout -b " + branch)
            runCommands("git push -u origin " + branch)

    def _devPushNewFile(self, filename, has_reviewer=True, has_plan=True):
        with phlsys_fs.chDirContext("developer"):
            reviewer = self.reviewer if has_reviewer else None
            plan = "testplan" if has_plan else None
            self._createCommitNewFileRaw(filename, plan, reviewer)
            runCommands("git push")

    def _acceptTheOnlyReview(self):
        # accept the review
        with phlsys_fs.chDirContext("phab"):
            clone = phlsys_git.GitClone(".")
            branches = phlgit_branch.getRemote(clone, "origin")
        wbList = abdt_naming.getWorkingBranches(branches)
        self.assertEqual(len(wbList), 1)
        wb = wbList[0]
        with phlsys_conduit.actAsUserContext(self.conduit, self.reviewer):
            phlcon_differential.createComment(
                self.conduit, wb.id, action="accept")

    def test_nothingToDo(self):
        # nothing to process
        processUpdatedRepo(self.conduit, "phab", "origin")

    def test_simpleWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/change/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

    def test_badMsgWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/change/master")
        self._devPushNewFile("NEWFILE", has_plan=False)
        self._phabUpdateWithExpectations(total=1, bad=1)
        self._devPushNewFile("NEWFILE2", has_plan=False)
        self._phabUpdateWithExpectations(total=1, bad=1)
        self._devPushNewFile("NEWFILE3")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devResetBranchToMaster("ph-review/change/master")
        self._devPushNewFile("NEWFILE", has_plan=False)
        self._phabUpdateWithExpectations(total=1, bad=1)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

    def test_badBaseWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/change/blaster")
        self._devPushNewFile("NEWFILE", has_plan=False)
        self._phabUpdateWithExpectations(total=1, bad=1)

        # delete the bad branch
        with phlsys_fs.chDirContext("developer"):
            runCommands("git push origin :ph-review/change/blaster")

        self._phabUpdateWithExpectations(total=0, bad=0)

    def test_badAuthorWorkflow(self):
        self._devSetAuthorAccount(phldef_conduit.notauser)
        self._devCheckoutPushNewBranch("ph-review/change/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=1)
        self._devResetBranchToMaster("ph-review/change/master")
        self._devSetAuthorAccount(self.author_account)
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

    def test_abandonedWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/change/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)

        # abandon the review
        with phlsys_fs.chDirContext("phab"):
            clone = phlsys_git.GitClone(".")
            branches = phlgit_branch.getRemote(clone, "origin")
        wbList = abdt_naming.getWorkingBranches(branches)
        self.assertEqual(len(wbList), 1)
        wb = wbList[0]
        with phlsys_conduit.actAsUserContext(
                self.conduit, self.author_account.user):
            phlcon_differential.createComment(
                self.conduit, wb.id, action="abandon")
        print "** abandoned review " + str(wb.id)

        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

    def tearDown(self):
        os.chdir(self._saved_path)
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
