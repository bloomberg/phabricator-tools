"""Test suite for abdi_processrepo."""

import os
import unittest
import abdmail_mailer
import phlmail_mocksender
import abdt_commitmessage
import abdt_naming
import phlcon_differential
import phldef_conduit
import phlgit_branch
import phlgit_config
import phlgit_log
import phlsys_conduit
import phlsys_fs
import phlsys_git
import phlsys_subprocess
import abdi_processrepo

# factors affecting a review:
#  age of the revisions
#  editing the review page
#  new revisions on the review branch
#  rewriting history on the review branch
#  author names
#  author accounts
#  base branch
#  availability of the git repo
#  availability of the phabricator instance


def runCommands(*commands):
    phlsys_subprocess.run_commands(*commands)


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.reviewer = phldef_conduit.ALICE.user
        self.author_account = phldef_conduit.BOB
        self._saved_path = None
        self.conduit = None
        self.mailer = None
        self.mock_sender = None

    def _gitCommitAll(self, subject, testPlan, reviewer):
        reviewers = [reviewer] if reviewer else None
        message = abdt_commitmessage.make(subject, None, testPlan, reviewers)
        phlsys_subprocess.run("git", "commit", "-a", "-F", "-", stdin=message)

    def _createCommitNewFileRaw(
            self, filename, testPlan=None, reviewer=None, contents=""):
        with open(filename, "w") as f:
            f.write(contents)
        runCommands("git add " + filename)
        self._gitCommitAll("add " + filename, testPlan, reviewer)

    def _createCommitNewFile(self, filename, reviewer):
        runCommands("touch " + filename)
        runCommands("git add " + filename)
        self._gitCommitAll("add " + filename, "test plan", reviewer)

    def setUp(self):
        # TODO: just make a temp dir
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
        self._phabSetAuthorAccount(phldef_conduit.PHAB)

        with phlsys_fs.chdir_context("developer"):
            self._createCommitNewFile("README", self.reviewer)
            runCommands("git push origin master")

        with phlsys_fs.chdir_context("phab"):
            runCommands("git fetch origin -p")

        self.conduit = phlsys_conduit.Conduit(
            phldef_conduit.TEST_URI,
            phldef_conduit.PHAB.user,
            phldef_conduit.PHAB.certificate)

        self.mock_sender = phlmail_mocksender.MailSender()
        self.mailer = abdmail_mailer.Mailer(
            self.mock_sender,
            ["admin@server.test"],
            "http://server.fake/testrepo.git",
            "http://phabricator.server.fake/")

    def _countPhabWorkingBranches(self):
        with phlsys_fs.chdir_context("phab"):
            clone = phlsys_git.GitClone(".")
            branches = phlgit_branch.getRemote(clone, "origin")
        wbList = abdt_naming.getWorkingBranches(branches)
        return len(wbList)

    def _countPhabBadWorkingBranches(self):
        with phlsys_fs.chdir_context("phab"):
            clone = phlsys_git.GitClone(".")
            branches = phlgit_branch.getRemote(clone, "origin")
        wbList = abdt_naming.getWorkingBranches(branches)
        numBadBranches = 0
        for wb in wbList:
            if abdt_naming.isStatusBad(wb):
                numBadBranches += 1
        return numBadBranches

    def _phabUpdate(self):
        with phlsys_fs.chdir_context("phab"):
            runCommands("git fetch origin -p")
        abdi_processrepo.processUpdatedRepo(
            self.conduit, "phab", "origin", self.mailer)

    def _phabUpdateWithExpectationsHelper(
            self, total=None, bad=None, emails=None):
        abdi_processrepo.processUpdatedRepo(
            self.conduit, "phab", "origin", self.mailer)
        if total is not None:
            self.assertEqual(self._countPhabWorkingBranches(), total)
        if bad is not None:
            self.assertEqual(self._countPhabBadWorkingBranches(), bad)
        if emails is not None:
            self.assertEqual(len(self.mock_sender.mails), emails)

    def _phabUpdateWithExpectations(self, total=None, bad=None, emails=None):
        with phlsys_fs.chdir_context("phab"):
            runCommands("git fetch origin -p")

        # multiple updates should have the same result if we are
        # not fetching and assuming the data in Phabricator
        # doesn't change.
        self._phabUpdateWithExpectationsHelper(total, bad, emails)
        self._phabUpdateWithExpectationsHelper(total, bad, emails)
        self._phabUpdateWithExpectationsHelper(total, bad, emails)

    def _devSetAuthorAccount(self, account):
        devClone = phlsys_git.GitClone("developer")
        phlgit_config.setUsernameEmail(devClone, account.user, account.email)

    def _phabSetAuthorAccount(self, account):
        devClone = phlsys_git.GitClone("phab")
        phlgit_config.setUsernameEmail(devClone, account.user, account.email)

    def _devResetBranchToMaster(self, branch):
        with phlsys_fs.chdir_context("developer"):
            runCommands("git reset origin/master --hard")
            runCommands("git push -u origin " + branch + " --force")

    def _devCheckoutPushNewBranch(self, branch):
        with phlsys_fs.chdir_context("developer"):
            runCommands("git checkout -b " + branch)
            runCommands("git push -u origin " + branch)

    def _devPushNewFile(
            self, filename, has_reviewer=True, has_plan=True, contents=""):
        with phlsys_fs.chdir_context("developer"):
            reviewer = self.reviewer if has_reviewer else None
            plan = "testplan" if has_plan else None
            self._createCommitNewFileRaw(filename, plan, reviewer, contents)
            runCommands("git push")

    def _getTheOnlyReviewId(self):
        with phlsys_fs.chdir_context("phab"):
            clone = phlsys_git.GitClone(".")
            branches = phlgit_branch.getRemote(clone, "origin")
        wbList = abdt_naming.getWorkingBranches(branches)
        self.assertEqual(len(wbList), 1)
        wb = wbList[0]
        return wb.id

    def _actOnTheOnlyReview(self, user, action):
        # accept the review
        reviewid = self._getTheOnlyReviewId()
        with phlsys_conduit.act_as_user_context(self.conduit, user):
            phlcon_differential.create_comment(
                self.conduit, reviewid, action=action)

    def _acceptTheOnlyReview(self):
        self._actOnTheOnlyReview(self.reviewer, "accept")

    def test_nothingToDo(self):
        # nothing to process
        abdi_processrepo.processUpdatedRepo(
            self.conduit, "phab", "origin", self.mailer)

    def test_simpleWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/simpleWorkflow/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

        # check the author on master
        with phlsys_fs.chdir_context("developer"):
            runCommands("git fetch -p", "git checkout master")
            clone = phlsys_git.GitClone(".")
            head = phlgit_log.getLastCommitHash(clone)
            authors = phlgit_log.getAuthorNamesEmailsFromHashes(clone, [head])
            author = authors[0]
            name = author[0]
            email = author[1]
            self.assertEqual(self.author_account.user, name)
            self.assertEqual(self.author_account.email, email)

    def test_badMsgWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/badMsgWorkflow/master")
        self._devPushNewFile("NEWFILE", has_plan=False)
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_noReviewerWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/noReviewerWorkflow/master")
        self._devPushNewFile("NEWFILE", has_reviewer=False)
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_badBaseWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/badBaseWorkflow/blaster")
        self._devPushNewFile("NEWFILE", has_plan=False)
        self._phabUpdateWithExpectations(total=1, bad=1)

        # delete the bad branch
        with phlsys_fs.chdir_context("developer"):
            runCommands("git push origin :ph-review/badBaseWorkflow/blaster")

        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_noBaseWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/noBaseWorkflow")
        self._devPushNewFile("NEWFILE", has_plan=False)

        # TODO: handle no base properly
        # self._phabUpdateWithExpectations(total=1, bad=1)

        # delete the bad branch
        with phlsys_fs.chdir_context("developer"):
            runCommands("git push origin :ph-review/noBaseWorkflow")

        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    # TODO: test_notBasedWorkflow
    # TODO: test_noCommitWorkflow

    def test_badAuthorWorkflow(self):
        self._devSetAuthorAccount(phldef_conduit.notauser)
        self._devCheckoutPushNewBranch("ph-review/badAuthorWorkflow/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=1, emails=1)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=1, emails=2)
        self._devResetBranchToMaster("ph-review/badAuthorWorkflow/master")
        self._devSetAuthorAccount(self.author_account)
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0, emails=2)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=2)

    def test_abandonedWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/abandonedWorkflow/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._actOnTheOnlyReview(self.author_account.user, "abandon")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_emptyMergeWorkflow(self):
        self._devCheckoutPushNewBranch("temp/emptyMerge/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to master and land a conflicting change
        with phlsys_fs.chdir_context("developer"):
            runCommands("git checkout master")
        self._devCheckoutPushNewBranch("ph-review/emptyMerge/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to original and try to push and land
        with phlsys_fs.chdir_context("developer"):
            runCommands("git checkout temp/emptyMerge/master")
        self._devCheckoutPushNewBranch("ph-review/emptyMerge2/master")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=1, bad=1)

        # 'resolve' by abandoning our change
        with phlsys_fs.chdir_context("developer"):
            runCommands("git push origin :ph-review/emptyMerge2/master")
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_mergeConflictWorkflow(self):
        self._devCheckoutPushNewBranch("temp/mergeConflict/master")
        self._devPushNewFile("NEWFILE", contents="hello")
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to master and land a conflicting change
        with phlsys_fs.chdir_context("developer"):
            runCommands("git checkout master")
        self._devCheckoutPushNewBranch("ph-review/mergeConflict/master")
        self._devPushNewFile("NEWFILE", contents="goodbye")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to original and try to push and land
        with phlsys_fs.chdir_context("developer"):
            runCommands("git checkout temp/mergeConflict/master")
        self._devCheckoutPushNewBranch("ph-review/mergeConflict2/master")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=1, bad=1)

        # 'resolve' by forcing our change through
        print "force our change"
        with phlsys_fs.chdir_context("developer"):
            runCommands("git fetch -p")
            runCommands("git merge origin/master -s ours")
            runCommands("git push origin ph-review/mergeConflict2/master")
        print "update again"
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_changeAlreadyMergedOnBase(self):
        self._devCheckoutPushNewBranch("landing_branch")
        self._devPushNewFile("NEWFILE")
        self._devCheckoutPushNewBranch(
            "ph-review/alreadyMerged/landing_branch")
        self._phabUpdateWithExpectations(total=1, bad=1)

        # reset the landing branch back to master to resolve
        with phlsys_fs.chdir_context("developer"):
            runCommands("git checkout landing_branch")
            runCommands("git reset origin/master --hard")
            runCommands("git push origin landing_branch --force")

        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_commandeeredUpdate(self):
        self._devCheckoutPushNewBranch("ph-review/commandeeredUpdate/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)

        reviewid = self._getTheOnlyReviewId()
        with phlsys_conduit.act_as_user_context(
                self.conduit,
                phldef_conduit.ALICE.user) as conduit:
            phlcon_differential.create_comment(
                conduit,
                reviewid,
                action=phlcon_differential.Action.claim)

        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)

    def test_commandeeredLand(self):
        self._devCheckoutPushNewBranch("ph-review/commandeeredLand/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)

        reviewid = self._getTheOnlyReviewId()
        with phlsys_conduit.act_as_user_context(
                self.conduit,
                phldef_conduit.PHAB.user) as conduit:
            phlcon_differential.create_comment(
                conduit,
                reviewid,
                action=phlcon_differential.Action.claim)

        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_createHugeReview(self):
        self._devCheckoutPushNewBranch("ph-review/createHugeReview/master")
        lots = "h\n" * 1 * 1024 * 1024
        self._devPushNewFile("NEWFILE", contents=lots)
        self._phabUpdateWithExpectations(total=1, bad=1)
        self._phabUpdateWithExpectations(total=1, bad=1)

    def test_hugeUpdateToReview(self):
        self._devCheckoutPushNewBranch("ph-review/hugeUpdateReview/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        lots = "h\n" * 1 * 1024 * 1024
        self._devPushNewFile("NEWFILE2", contents=lots)
        self._phabUpdateWithExpectations(total=1, bad=1)
        self._phabUpdateWithExpectations(total=1, bad=1)

    # TODO: test landing when origin has been updated underneath us
    # TODO: test landing when dependent review hasn't been landed

    def tearDown(self):
        os.chdir(self._saved_path)
        runCommands("rm -rf abd-test")

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
