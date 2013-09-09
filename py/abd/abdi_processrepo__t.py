"""Test suite for abdi_processrepo."""

from __future__ import absolute_import

import contextlib
import types
import unittest

import phlcon_differential
import phldef_conduit
import phlmail_mocksender
import phlsys_pluginmanager

import abdmail_mailer
import abdt_branchmock
import abdt_conduitmock
import abdt_exception
import abdt_naming
import abdt_reporeporter
import abdtst_devphabgit

import abdi_processrepo

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] processUpdateRepo can handle the case of no branches
# [ B] processUpdateRepo can create, update and land an uncomplicated review
# [ C] processUpdateRepo can handle a review without test plan
# [ D] processUpdateRepo can handle a review being closed unexpectedly
# [ E] processUpdateRepo can handle a review without initial valid base
# [ F] processUpdateRepo can handle a review without initial author
# [ G] processUpdateRepo can handle a review without commits on branch
# [ H] processUpdateRepo can abandon a review when the branch disappears
# [ I] processUpdateRepo can handle a review with merge conflicts
# [ J] processUpdateRepo can handle a diff that's too big
# [ K] processUpdateRepo can report an exception during branch processing
# [ B] processUpdateRepo doesn't leave the current branch set after processing
# [  ] processUpdateRepo can handle a review without commits in repo
# [  ] processUpdateRepo will comment on a bad branch if the error has changed
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_Uncomplicated
# [ C] test_C_NoTestPlan
# [ D] test_D_UnexpectedClose
# [ E] test_E_InvalidBaseBranch
# [ F] test_F_NoInitialAuthor
# [ G] test_G_NoCommitsOnBranch
# [ H] test_H_AbandonRemovedBranch
# [ I] test_I_MergeConflicts
# [ J] test_J_DiffTooBig
# [ K] test_K_ExceptionDuringProcessing
#==============================================================================


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.conduit_data = None
        self.conduit = None
        self.mock_sender = None
        self.mailer = None
        self.plugin_manager = None
        self.reporter = None
        self.reporter_try = None
        self.reporter_ok = None

    def setUp(self):
        self.conduit_data = abdt_conduitmock.ConduitMockData()
        self.conduit = abdt_conduitmock.ConduitMock(self.conduit_data)
        self.mock_sender = phlmail_mocksender.MailSender()
        self.mailer = abdmail_mailer.Mailer(
            self.mock_sender,
            ["admin@server.test"],
            "http://server.fake/testrepo.git",
            "http://phabricator.server.fake/")
        self.plugin_manager = phlsys_pluginmanager.PluginManager([], [])
        self.reporter_try = {}
        self.reporter_ok = {}
        self.reporter = abdt_reporeporter.RepoReporter(
            'abdi_processrepo__t:Test repo',
            'http://my.phabricator/{review}',
            'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}',
            abdt_reporeporter.SharedDictOutput(self.reporter_try),
            abdt_reporeporter.SharedDictOutput(self.reporter_ok))

    def tearDown(self):
        pass

    def _process_branches(self, branches):
        with contextlib.closing(self.reporter):
            abdi_processrepo.process_branches(
                branches,
                self.conduit,
                self.mailer,
                self.plugin_manager,
                self.reporter)

    def test_A_Breathing(self):
        self._process_branches([])
        self.assertTrue(self.mock_sender.is_empty())
        self.assertTrue(self.conduit_data.is_unchanged())

    def test_B_Uncomplicated(self):
        branch, branch_data = abdt_branchmock.create_simple_new_review()
        self._process_branches([branch])
        self.assertFalse(branch.is_status_bad())
        self.assertTrue(self.mock_sender.is_empty())
        self.assertFalse(self.conduit_data.is_unchanged())
        self.assertEqual(len(self.conduit_data.revisions), 1)
        self.assertFalse(
            self.reporter_try[abdt_reporeporter.REPO_ATTRIB_STATUS_BRANCH])

        self.conduit_data.accept_the_only_review()
        self.conduit_data.set_unchanged()
        self._process_branches([branch])
        self.assertEqual(len(self.conduit_data.revisions), 1)
        self.assertTrue(self.conduit_data.revisions[0].is_closed())
        self.assertTrue(self.mock_sender.is_empty())
        self.assertFalse(self.conduit_data.is_unchanged())
        self.assertTrue(branch.is_new())
        self.assertFalse(
            self.reporter_try[abdt_reporeporter.REPO_ATTRIB_STATUS_BRANCH])

    def test_C_NoTestPlan(self):
        branch, branch_data = abdt_branchmock.create_simple_new_review()

        def error_parse_commit_message(self, unused_message):
            return phlcon_differential.ParseCommitMessageResponse(
                fields=None, errors=["FAKE ERROR"])

        regular_parse = self.conduit.parse_commit_message
        self.conduit.parse_commit_message = types.MethodType(
            error_parse_commit_message, self.conduit)

        self._process_branches([branch])

        self.assertEqual(len(self.conduit_data.revisions), 1)
        self.assertFalse(self.conduit_data.revisions[0].is_closed())
        self.assertTrue(self.mock_sender.is_empty())
        self.assertFalse(self.conduit_data.is_unchanged())
        self.assertTrue(branch.is_status_bad())

        self.conduit.parse_commit_message = regular_parse
        self.conduit_data.set_unchanged()
        branch_data.has_new_commits = True

        self.conduit_data.accept_the_only_review()
        self._process_branches([branch])

        self.assertEqual(len(self.conduit_data.revisions), 1)
        self.assertTrue(self.conduit_data.revisions[0].is_closed())
        self.assertTrue(self.mock_sender.is_empty())
        self.assertFalse(self.conduit_data.is_unchanged())

    def test_D_UnexpectedClose(self):
        branch, branch_data = abdt_branchmock.create_simple_new_review()
        self._process_branches([branch])

        revision = self.conduit_data.get_revision(branch_data.revision_id)
        revision.set_closed()
        branch_data.has_new_commits = True

        self._process_branches([branch])
        self.assertTrue(branch.is_status_bad())

    def test_E_InvalidBaseBranch(self):
        # set base to invalid
        branch, branch_data = abdt_branchmock.create_new_review_invalid_base()
        self._process_branches([branch])
        self.assertTrue(branch.is_status_bad())

        # set base ok again
        branch_data.is_base_ok = True
        self._process_branches([branch])
        self.assertFalse(branch.is_status_bad())

        # set base bad again
        branch_data.is_base_ok = False
        branch_data.has_new_commits = True
        self._process_branches([branch])
        self.assertTrue(branch.is_status_bad())

    def test_F_NoInitialAuthor(self):
        branch, branch_data = abdt_branchmock.create_review_no_initial_author()
        self._process_branches([branch])
        self.assertTrue(branch.is_status_bad_pre_review())

        # we must have sent a message to warn about the user
        self.assertFalse(self.mock_sender.is_empty())

        # no review will have been created
        self.assertTrue(self.conduit_data.is_unchanged())

        # fix the user details and process
        branch_data.names_emails = abdt_branchmock.create_ok_names_emails()
        branch_data.has_new_commits = True
        self._process_branches([branch])
        self.assertFalse(branch.is_status_bad())

        # check that a review was created
        self.assertFalse(self.conduit_data.is_unchanged())
        self.assertEqual(len(self.conduit_data.revisions), 1)

    def test_G_NoCommitsOnBranch(self):
        branch, branch_data = abdt_branchmock.create_review_no_commits()
        self._process_branches([branch])
        self.assertTrue(branch.is_status_bad())

    def test_H_AbandonRemovedBranch(self):
        branch, branch_data = abdt_branchmock.create_review_removed()
        self._process_branches([branch])
        self.assertTrue(branch.is_null())

        # TODO: should probably abandon the review too, if the branch goes
        # self.assertTrue(
        #     self.conduit_data.get_the_only_revision().is_abandoned())

    def test_I_MergeConflicts(self):

        def error_land(self, unused_name, unused_email, unused_message):
            raise abdt_exception.LandingException(
                'landing exception',
                '<review branch name>',
                '<base branch name>')

        # create review ok
        branch, branch_data = abdt_branchmock.create_simple_new_review()
        self._process_branches([branch])

        # fail to land
        old_land = branch.land
        branch.land = types.MethodType(error_land, branch)
        self.conduit_data.accept_the_only_review()
        self._process_branches([branch])
        self.assertTrue(branch.is_status_bad_land())

        # fix the landing error
        branch.land = old_land
        branch_data.has_new_commits = True

        # land ok
        self.conduit_data.accept_the_only_review()
        self._process_branches([branch])
        self.assertTrue(branch.is_null())

    def test_J_DiffTooBig(self):

        def error_diff(self):
            raise abdt_exception.LargeDiffException("diff too big", 100, 10)

        # fail to create review
        branch, branch_data = abdt_branchmock.create_simple_new_review()
        old_diff = branch.make_raw_diff
        branch.make_raw_diff = types.MethodType(error_diff, branch)
        self._process_branches([branch])
        self.assertFalse(branch.is_status_bad_pre_review())
        self.assertFalse(branch.is_status_bad_land())
        self.assertTrue(branch.is_status_bad())

        # fix the large diff
        branch.make_raw_diff = old_diff
        branch_data.has_new_commits = True

        # update the review ok
        self._process_branches([branch])
        self.assertFalse(branch.is_status_bad())

        # land ok
        self.conduit_data.accept_the_only_review()
        self._process_branches([branch])
        self.assertTrue(branch.is_null())

    def test_K_ExceptionDuringProcessing(self):

        class test_K_ExceptionDuringProcessing_Exception(Exception):
            pass

        def error_diff(self):
            raise test_K_ExceptionDuringProcessing_Exception()

        # fail to create review
        branch, branch_data = abdt_branchmock.create_simple_new_review()
        branch.make_raw_diff = types.MethodType(error_diff, branch)

        # make sure it raises our exception
        self.assertRaises(
            test_K_ExceptionDuringProcessing_Exception,
            self._process_branches,
            [branch])

        # make sure the current branch is set in the report
        self.assertEqual(
            self.reporter_try[abdt_reporeporter.REPO_ATTRIB_STATUS_BRANCH],
            branch.review_branch_name())


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


class OldTest(unittest.TestCase):

    def __init__(self, data):
        super(OldTest, self).__init__(data)
        self.reviewer = phldef_conduit.ALICE.user
        self.author_account = phldef_conduit.BOB
        self.conduit = None
        self.clone = None
        self.dev_phab = None
        self.mailer = None
        self.mock_sender = None
        self.plugin_manager = None
        self.reporter = None
        self.reporter_try = None
        self.reporter_ok = None

    def setUp(self):
        self.dev_phab = abdtst_devphabgit.Collaboration(
            self.author_account, phldef_conduit.PHAB)

        self.clone = self.dev_phab.clone

        self.dev_phab.dev_commit_new_file("README")
        self.dev_phab.dev_push_branch("master")
        self.dev_phab.phab_fetch()

        self.reporter_try = {}
        self.reporter_ok = {}
        self.reporter = abdt_reporeporter.RepoReporter(
            'abdi_processrepo__t:OldTest repo',
            'http://my.phabricator/{review}',
            'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}',
            abdt_reporeporter.SharedDictOutput(self.reporter_try),
            abdt_reporeporter.SharedDictOutput(self.reporter_ok))

        # sys_conduit = phlsys_conduit.Conduit(
        #     phldef_conduit.TEST_URI,
        #     phldef_conduit.PHAB.user,
        #     phldef_conduit.PHAB.certificate)

        # self.conduit = abdt_conduit.Conduit(sys_conduit)
        self.conduit = abdt_conduitmock.ConduitMock()

        self.mock_sender = phlmail_mocksender.MailSender()
        self.mailer = abdmail_mailer.Mailer(
            self.mock_sender,
            ["admin@server.test"],
            "http://server.fake/testrepo.git",
            "http://phabricator.server.fake/")
        # Default behavior is to not test with plugins
        self.plugin_manager = phlsys_pluginmanager.PluginManager([], [])

    def _phabUpdate(self):
        self.dev_phab.phab_fetch()
        abdi_processrepo.process_branches(
            self.clone.get_managed_branches(), self.conduit,
            self.mailer, self.plugin_manager, self.reporter)

    def _phabUpdateWithExpectationsHelper(
            self, total=None, bad=None, emails=None):
        abdi_processrepo.process_branches(
            self.clone.get_managed_branches(), self.conduit,
            self.mailer, self.plugin_manager, self.reporter)
        if total is not None:
            self.assertEqual(
                self.dev_phab.count_phab_working_branches(), total)
        if bad is not None:
            self.assertEqual(
                self.dev_phab.count_phab_bad_working_branches(), bad)
        if emails is not None:
            self.assertEqual(len(self.mock_sender.mails), emails)

    def _phabUpdateWithExpectations(self, total=None, bad=None, emails=None):
        self.dev_phab.phab_fetch()

        # multiple updates should have the same result if we are
        # not fetching and assuming the data in Phabricator
        # doesn't change.
        self._phabUpdateWithExpectationsHelper(total, bad, emails)
        self._phabUpdateWithExpectationsHelper(total, bad, emails)
        self._phabUpdateWithExpectationsHelper(total, bad, emails)

    def _devSetAuthorAccount(self, account):
        self.dev_phab.dev_clone.set_name_email(account.user, account.email)

    def _phabSetAuthorAccount(self, account):
        self.clone.set_name_email(account.user, account.email)

    def _devPushNewFile(
            self, filename, has_reviewer=True, has_plan=True, contents=""):
        reviewer = self.reviewer if has_reviewer else None
        plan = "testplan" if has_plan else None
        self.dev_phab.dev_commit_new_file(filename, plan, reviewer, contents)
        self.dev_phab.dev_push()

    def _getTheOnlyReviewId(self):
        branches = self.clone.get_remote_branches()
        wbList = abdt_naming.getWorkingBranches(branches)
        self.assertEqual(len(wbList), 1)
        wb = wbList[0]
        return wb.id

    def _acceptTheOnlyReview(self):
        reviewid = self._getTheOnlyReviewId()
        self.conduit.accept_revision_as_user(reviewid, self.reviewer)

    def _abandonTheOnlyReview(self):
        reviewid = self._getTheOnlyReviewId()
        self.conduit.abandon_revision(reviewid)

    def test_nothingToDo(self):
        # nothing to process
        abdi_processrepo.process_branches(
            self.clone.get_managed_branches(), self.conduit,
            self.mailer, self.plugin_manager, self.reporter)

    def test_simpleWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/simpleWorkflow/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_badMsgWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/badMsgWorkflow/master")
        self._devPushNewFile("NEWFILE", has_plan=False)
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_noReviewerWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/noReviewerWorkflow/master")
        self._devPushNewFile("NEWFILE", has_reviewer=False)
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_badBaseWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/badBaseWorkflow/blaster")
        self._devPushNewFile("NEWFILE", has_plan=False)
        self._phabUpdateWithExpectations(total=1, bad=1)

        # delete the bad branch
        self.dev_phab.dev_push_delete_branch(
            "arcyd-review/badBaseWorkflow/blaster")

        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_withReservedBranch(self):
        self.dev_phab.dev_checkout_push_new_branch("dev/arcyd/reserve")
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/reserve/master")
        self._devPushNewFile("reserve")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_noBaseWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/noBaseWorkflow")
        self._devPushNewFile("NEWFILE", has_plan=False)

        # TODO: handle no base properly
        # self._phabUpdateWithExpectations(total=1, bad=1)

        # delete the bad branch
        self.dev_phab.dev_push_delete_branch("arcyd-review/noBaseWorkflow")

        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    # TODO: test_notBasedWorkflow
    # TODO: test_noCommitWorkflow

    def test_badAuthorWorkflow(self):
        self._devSetAuthorAccount(phldef_conduit.NOTAUSER)
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/badAuthorWorkflow/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=1, emails=1)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=1, emails=2)
        self.dev_phab.dev_reset_branch_to_master(
            "arcyd-review/badAuthorWorkflow/master")
        self._devSetAuthorAccount(self.author_account)
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0, emails=2)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=2)

    def test_abandonedWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/abandonedWorkflow/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._abandonTheOnlyReview()
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_emptyMergeWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch("temp/emptyMerge/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to master and land a conflicting change
        self.dev_phab.dev_checkout("master")
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/emptyMerge/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to original and try to push and land
        self.dev_phab.dev_checkout("temp/emptyMerge/master")
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/emptyMerge2/master")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=1, bad=1)

        # 'resolve' by abandoning our change
        self.dev_phab.dev_push_delete_branch("arcyd-review/emptyMerge2/master")
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_mergeConflictWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch("temp/mergeConflict/master")
        self._devPushNewFile("NEWFILE", contents="hello")
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to master and land a conflicting change
        self.dev_phab.dev_checkout("master")
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/mergeConflict/master")
        self._devPushNewFile("NEWFILE", contents="goodbye")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to original and try to push and land
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/mergeConflict2/master",
            base="temp/mergeConflict/master")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=1, bad=1)

        # 'resolve' by forcing our change through
        print "force our change"
        self.dev_phab.dev_fetch()
        self.dev_phab.dev_merge_keep_ours("origin/master")
        self.dev_phab.dev_push_branch("arcyd-review/mergeConflict2/master")

        print "update again"
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_changeAlreadyMergedOnBase(self):
        self.dev_phab.dev_checkout_push_new_branch("landing_branch")
        self._devPushNewFile("NEWFILE")
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/alreadyMerged/landing_branch")
        self._phabUpdateWithExpectations(total=1, bad=1)

        # reset the landing branch back to master to resolve
        self.dev_phab.dev_reset_branch_to_master("landing_branch")

        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_commandeeredUpdate(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/commandeeredUpdate/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)

        reviewid = self._getTheOnlyReviewId()
        self.conduit.commandeer_revision_as_user(
            reviewid, phldef_conduit.ALICE.user)

        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)

    def test_commandeeredLand(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/commandeeredLand/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)

        reviewid = self._getTheOnlyReviewId()
        self.conduit.commandeer_revision_as_user(
            reviewid, phldef_conduit.PHAB.user)

        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_createHugeReview(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/createHugeReview/master")
        lots = "h\n" * 1 * 1024 * 1024
        self._devPushNewFile("NEWFILE", contents=lots)
        self._phabUpdateWithExpectations(total=1, bad=1)

    def test_hugeUpdateToReview(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/hugeUpdateReview/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        lots = "h\n" * 1 * 1024 * 1024
        self._devPushNewFile("NEWFILE2", contents=lots)
        self._phabUpdateWithExpectations(total=1, bad=1)

    def test_emptyCommit(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "arcyd-review/emptyCommit/master")
        self.dev_phab.dev_commit_allow_empty('emptyCommit')
        self.dev_phab.dev_push()
        self._phabUpdateWithExpectations(total=1, bad=1)

    def tearDown(self):
        self.dev_phab.close()

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
