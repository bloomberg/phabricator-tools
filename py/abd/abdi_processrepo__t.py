"""Test suite for abdi_processrepo."""

import unittest

import phldef_conduit
import phlmail_mocksender
# import phlsys_conduit

import abdi_processrepo
import abdmail_mailer
# import abdt_conduit
import abdt_branchmock
import abdt_conduitmock
import abdt_naming
import abdtst_devphabgit


#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] processUpdateRepo can handle the case of no branches
# [  ] processUpdateRepo can create, update and land an uncomplicated review
# [  ] processUpdateRepo can handle a review without test plan
# [  ] processUpdateRepo can handle a review without initial reviewer
# [  ] processUpdateRepo can handle a review without initial valid base
# [  ] processUpdateRepo can handle a review without initial author
# [  ] processUpdateRepo can abandon a review when the branch disappears
# [  ] processUpdateRepo can handle a review with merge conflicts
#
# for testing 'branch'
# [  ] XXX: withReservedBranch
# [  ] XXX: emptyMergeWorkflow
# [  ] XXX: mergeConflictWorkflow
# [  ] XXX: changeAlreadyMergedOnBase
# [  ] XXX: commandeeredLand
# [  ] XXX: createHugeReview
# [  ] XXX: hugeUpdateToReview

# for testing 'conduit'
# [  ] XXX: commandeeredUpdate
# [  ] XXX: commandeeredLand
# [  ] XXX: createHugeReview
# [  ] XXX: hugeUpdateToReview
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# XXX: fill in the others
#==============================================================================


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.conduit = None
        self.mock_sender = None
        self.mailer = None

    def setUp(self):
        self.conduit = abdt_conduitmock.ConduitMock()
        self.mock_sender = phlmail_mocksender.MailSender()
        self.mailer = abdmail_mailer.Mailer(
            self.mock_sender,
            ["admin@server.test"],
            "http://server.fake/testrepo.git",
            "http://phabricator.server.fake/")

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        abdi_processrepo.process_branches([], self.conduit, self.mailer)
        self.assertTrue(self.mock_sender.is_empty())
        self.assertTrue(self.conduit.is_unchanged())

    def test_B_Uncomplicated(self):
        branch = abdt_branchmock.create_simple_new_review()
        abdi_processrepo.process_branches([branch], self.conduit, self.mailer)
        self.assertFalse(branch.is_status_bad())
        self.assertTrue(self.mock_sender.is_empty())
        self.assertFalse(self.conduit.is_unchanged())


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

    def setUp(self):
        self.dev_phab = abdtst_devphabgit.Collaboration(
            self.author_account, phldef_conduit.PHAB)

        self.clone = self.dev_phab.clone

        self.dev_phab.dev_commit_new_file("README")
        self.dev_phab.dev_push_branch("master")
        self.dev_phab.phab_fetch()

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

    def _phabUpdate(self):
        self.dev_phab.phab_fetch()
        abdi_processrepo.process_branches(
            self.clone.get_managed_branches(), self.conduit, self.mailer)

    def _phabUpdateWithExpectationsHelper(
            self, total=None, bad=None, emails=None):
        abdi_processrepo.process_branches(
            self.clone.get_managed_branches(), self.conduit, self.mailer)
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
            self.clone.get_managed_branches(), self.conduit, self.mailer)

    def test_simpleWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/simpleWorkflow/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_badMsgWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/badMsgWorkflow/master")
        self._devPushNewFile("NEWFILE", has_plan=False)
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_noReviewerWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/noReviewerWorkflow/master")
        self._devPushNewFile("NEWFILE", has_reviewer=False)
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_badBaseWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/badBaseWorkflow/blaster")
        self._devPushNewFile("NEWFILE", has_plan=False)
        self._phabUpdateWithExpectations(total=1, bad=1)

        # delete the bad branch
        self.dev_phab.dev_push_delete_branch(
            "ph-review/badBaseWorkflow/blaster")

        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_withReservedBranch(self):
        self.dev_phab.dev_checkout_push_new_branch("dev/phab/reserve")
        self.dev_phab.dev_checkout_push_new_branch("ph-review/reserve/master")
        self._devPushNewFile("reserve")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_noBaseWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch("ph-review/noBaseWorkflow")
        self._devPushNewFile("NEWFILE", has_plan=False)

        # TODO: handle no base properly
        # self._phabUpdateWithExpectations(total=1, bad=1)

        # delete the bad branch
        self.dev_phab.dev_push_delete_branch("ph-review/noBaseWorkflow")

        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    # TODO: test_notBasedWorkflow
    # TODO: test_noCommitWorkflow

    def test_badAuthorWorkflow(self):
        self._devSetAuthorAccount(phldef_conduit.NOTAUSER)
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/badAuthorWorkflow/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=1, emails=1)
        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=1, emails=2)
        self.dev_phab.dev_reset_branch_to_master(
            "ph-review/badAuthorWorkflow/master")
        self._devSetAuthorAccount(self.author_account)
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0, emails=2)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=2)

    def test_abandonedWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/abandonedWorkflow/master")
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
            "ph-review/emptyMerge/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to original and try to push and land
        self.dev_phab.dev_checkout("temp/emptyMerge/master")
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/emptyMerge2/master")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=1, bad=1)

        # 'resolve' by abandoning our change
        self.dev_phab.dev_push_delete_branch("ph-review/emptyMerge2/master")
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_mergeConflictWorkflow(self):
        self.dev_phab.dev_checkout_push_new_branch("temp/mergeConflict/master")
        self._devPushNewFile("NEWFILE", contents="hello")
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to master and land a conflicting change
        self.dev_phab.dev_checkout("master")
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/mergeConflict/master")
        self._devPushNewFile("NEWFILE", contents="goodbye")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0)

        # move back to original and try to push and land
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/mergeConflict2/master",
            base="temp/mergeConflict/master")
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=1, bad=1)

        # 'resolve' by forcing our change through
        print "force our change"
        self.dev_phab.dev_fetch()
        self.dev_phab.dev_merge_keep_ours("origin/master")
        self.dev_phab.dev_push_branch("ph-review/mergeConflict2/master")

        print "update again"
        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_changeAlreadyMergedOnBase(self):
        self.dev_phab.dev_checkout_push_new_branch("landing_branch")
        self._devPushNewFile("NEWFILE")
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/alreadyMerged/landing_branch")
        self._phabUpdateWithExpectations(total=1, bad=1)

        # reset the landing branch back to master to resolve
        self.dev_phab.dev_reset_branch_to_master("landing_branch")

        self._phabUpdateWithExpectations(total=1, bad=0)
        self._acceptTheOnlyReview()
        self._phabUpdateWithExpectations(total=0, bad=0, emails=0)

    def test_commandeeredUpdate(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/commandeeredUpdate/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)

        reviewid = self._getTheOnlyReviewId()
        self.conduit.commandeer_revision_as_user(
            reviewid, phldef_conduit.ALICE.user)

        self._devPushNewFile("NEWFILE2")
        self._phabUpdateWithExpectations(total=1, bad=0)

    def test_commandeeredLand(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/commandeeredLand/master")
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
            "ph-review/createHugeReview/master")
        lots = "h\n" * 1 * 1024 * 1024
        self._devPushNewFile("NEWFILE", contents=lots)
        self._phabUpdateWithExpectations(total=1, bad=1)

    def test_hugeUpdateToReview(self):
        self.dev_phab.dev_checkout_push_new_branch(
            "ph-review/hugeUpdateReview/master")
        self._devPushNewFile("NEWFILE")
        self._phabUpdateWithExpectations(total=1, bad=0)
        lots = "h\n" * 1 * 1024 * 1024
        self._devPushNewFile("NEWFILE2", contents=lots)
        self._phabUpdateWithExpectations(total=1, bad=1)

    # TODO: test landing when origin has been updated underneath us
    # TODO: test landing when dependent review hasn't been landed

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
