import os
import unittest
import abdmail_mailer
import abdmail_printsender
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


def runCommands(*commands):
    phlsys_subprocess.runCommands(*commands)


class TestAbd(unittest.TestCase):

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
        self._phabSetAuthorAccount(phldef_conduit.phab)

        with phlsys_fs.chDirContext("developer"):
            self._createCommitNewFile("README", self.reviewer)
            runCommands("git push origin master")

        with phlsys_fs.chDirContext("phab"):
            runCommands("git fetch origin -p")

        self.conduit = phlsys_conduit.Conduit(
            phldef_conduit.test_uri,
            phldef_conduit.phab.user,
            phldef_conduit.phab.certificate)

        print_sender = abdmail_printsender.MailSender("phab@server.test")
        self.mailer = abdmail_mailer.Mailer(
            print_sender,
            ["admin@server.test"],
            "http://server.fake/testrepo.git")

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
        abdi_processrepo.processUpdatedRepo(
            self.conduit, "phab", "origin", self.mailer)

    def _phabUpdateWithExpectations(self, total=None, bad=None):
        with phlsys_fs.chDirContext("phab"):
            runCommands("git fetch origin -p")
        abdi_processrepo.processUpdatedRepo(
            self.conduit, "phab", "origin", self.mailer)
        if total is not None:
            self.assertEqual(self._countPhabWorkingBranches(), total)
        if bad is not None:
            self.assertEqual(self._countPhabBadWorkingBranches(), bad)

    def _devSetAuthorAccount(self, account):
        devClone = phlsys_git.GitClone("developer")
        phlgit_config.setUsernameEmail(devClone, account.user, account.email)

    def _phabSetAuthorAccount(self, account):
        devClone = phlsys_git.GitClone("phab")
        phlgit_config.setUsernameEmail(devClone, account.user, account.email)

    def _devResetBranchToMaster(self, branch):
        with phlsys_fs.chDirContext("developer"):
            runCommands("git reset origin/master --hard")
            runCommands("git push -u origin " + branch + " --force")

    def _devCheckoutPushNewBranch(self, branch):
        with phlsys_fs.chDirContext("developer"):
            runCommands("git checkout -b " + branch)
            runCommands("git push -u origin " + branch)

    def _devPushNewFile(
            self, filename, has_reviewer=True, has_plan=True, contents=""):
        with phlsys_fs.chDirContext("developer"):
            reviewer = self.reviewer if has_reviewer else None
            plan = "testplan" if has_plan else None
            self._createCommitNewFileRaw(filename, plan, reviewer, contents)
            runCommands("git push")

    def _actOnTheOnlyReview(self, user, action):
        # accept the review
        with phlsys_fs.chDirContext("phab"):
            clone = phlsys_git.GitClone(".")
            branches = phlgit_branch.getRemote(clone, "origin")
        wbList = abdt_naming.getWorkingBranches(branches)
        self.assertEqual(len(wbList), 1)
        wb = wbList[0]
        with phlsys_conduit.actAsUserContext(self.conduit, user):
            phlcon_differential.createComment(
                self.conduit, wb.id, action=action)

    def _acceptTheOnlyReview(self):
        self._actOnTheOnlyReview(self.reviewer, "accept")

    def test_nothingToDo(self):
        # nothing to process
        abdi_processrepo.processUpdatedRepo(
            self.conduit, "phab", "origin", self.mailer)

    def test_simpleWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/change/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

        # check the author on master
        with phlsys_fs.chDirContext("developer"):
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

    def test_noReviewerWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/change/master")
        self._devPushNewFile("NEWFILE", has_reviewer=False)
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

    def test_noBaseWorkflow(self):
        self._devCheckoutPushNewBranch("ph-review/change")
        self._devPushNewFile("NEWFILE", has_plan=False)

        # TODO: handle no base properly
        #self._phabUpdateWithExpectations(total=1, bad=1)

        # delete the bad branch
        with phlsys_fs.chDirContext("developer"):
            runCommands("git push origin :ph-review/change")

        self._phabUpdateWithExpectations(total=0, bad=0)

    # TODO: test_notBasedWorkflow
    # TODO: test_noCommitWorkflow

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
        self._actOnTheOnlyReview(self.author_account.user, "abandon")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

    def test_emptyMergeWorkflow(self):
        self._devCheckoutPushNewBranch("temp/change/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to master and land a conflicting change
        with phlsys_fs.chDirContext("developer"):
            runCommands("git checkout master")
        self._devCheckoutPushNewBranch("ph-review/change/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to original and try to push and land
        with phlsys_fs.chDirContext("developer"):
            runCommands("git checkout temp/change/master")
        self._devCheckoutPushNewBranch("ph-review/change2/master")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=1, bad=1)

        # 'resolve' by abandoning our change
        with phlsys_fs.chDirContext("developer"):
            runCommands("git push origin :ph-review/change2/master")
        self._phabUpdateWithExpectations(total=0, bad=0)

    def test_mergeConflictWorkflow(self):
        self._devCheckoutPushNewBranch("temp/change/master")
        self._devPushNewFile("NEWFILE", contents="hello")
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to master and land a conflicting change
        with phlsys_fs.chDirContext("developer"):
            runCommands("git checkout master")
        self._devCheckoutPushNewBranch("ph-review/change/master")
        self._devPushNewFile("NEWFILE", contents="goodbye")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to original and try to push and land
        with phlsys_fs.chDirContext("developer"):
            runCommands("git checkout temp/change/master")
        self._devCheckoutPushNewBranch("ph-review/change2/master")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=1, bad=1)

        # 'resolve' by forcing our change through
        print "force our change"
        with phlsys_fs.chDirContext("developer"):
            runCommands("git fetch -p")
            runCommands("git merge origin/master -s ours")
            runCommands("git push origin ph-review/change2/master")
        print "update again"
        self._phabUpdateWithExpectations(total=1, bad=0)
        print "update last time"
        self._phabUpdateWithExpectations(total=0, bad=0)

    def test_changeAlreadyMergedOnBase(self):
        self._devCheckoutPushNewBranch("landing_branch")
        self._devPushNewFile("NEWFILE")
        self._devCheckoutPushNewBranch("ph-review/change/landing_branch")
        self._phabUpdateWithExpectations(total=1, bad=1)

        # reset the landing branch back to master to resolve
        with phlsys_fs.chDirContext("developer"):
            runCommands("git checkout landing_branch")
            runCommands("git reset origin/master --hard")
            runCommands("git push origin landing_branch --force")

        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

    def tearDown(self):
        os.chdir(self._saved_path)
        #runCommands("rm -rf abd-test")
        pass

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
