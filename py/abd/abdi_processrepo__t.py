"""Test suite for abdi_processrepo."""

from __future__ import absolute_import

import contextlib
import types
import unittest

import phlcon_differential
import phlmail_mocksender

import abdmail_mailer
import abdt_arcydreporter
import abdt_branchmock
import abdt_conduitmock
import abdt_exception
import abdt_repooptions
import abdt_reporeporter
import abdt_shareddictoutput

import abdi_processrepo

# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
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
# [ L] processUpdateRepo can handle a branch with only empty commits
# [ M] processUpdateRepo won't emit errors in a cycle when landing w/o author
# [  ] processUpdateRepo can handle a review without commits in repo
# [  ] processUpdateRepo will comment on a bad branch if the error has changed
# -----------------------------------------------------------------------------
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
# [ L] test_L_EmptyDiff
# [ M] test_M_NoLandingAuthor
# =============================================================================


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.conduit_data = None
        self.conduit = None
        self.mock_sender = None
        self.mailer = None
        self.arcyd_reporter_data = None
        self.arcyd_reporter = None
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
        self.arcyd_reporter_data = {}
        self.arcyd_reporter = abdt_arcydreporter.ArcydReporter(
            abdt_shareddictoutput.ToDict(self.arcyd_reporter_data),
            "arcyd@localhost")

    def tearDown(self):
        pass

    def _process_branches(self, branches):
        self.reporter_try = {}
        self.reporter_ok = {}

        config = abdt_repooptions.Data()
        config.branch_url_format = (
            'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}')
        config.review_url_format = 'http://my.phabricator/{review}'

        self.reporter = abdt_reporeporter.RepoReporter(
            self.arcyd_reporter,
            'abdi_processrepo__t:Test repo:machine name',
            'abdi_processrepo__t:Test repo',
            'org/repo',
            abdt_shareddictoutput.ToDict(self.reporter_try),
            abdt_shareddictoutput.ToDict(self.reporter_ok))

        self.reporter.set_config(config)

        with contextlib.closing(self.reporter):
            abdi_processrepo.process_branches(
                branches,
                self.conduit,
                self.mailer,
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

    def test_L_EmptyDiff(self):

        # fail to create review with empty diff
        branch, branch_data = abdt_branchmock.create_simple_new_review()
        branch_data.raw_diff = ""
        self._process_branches([branch])
        self.assertFalse(branch.is_status_bad_pre_review())
        self.assertFalse(branch.is_status_bad_land())
        self.assertTrue(branch.is_status_bad())

        # fix the empty diff
        branch_data.raw_diff = "raw diff"
        branch_data.has_new_commits = True
        self._process_branches([branch])
        self.assertFalse(branch.is_status_bad())

        # empty diff again
        branch_data.raw_diff = ""
        branch_data.has_new_commits = True
        self._process_branches([branch])
        self.assertFalse(branch.is_status_bad_pre_review())
        self.assertFalse(branch.is_status_bad_land())
        self.assertTrue(branch.is_status_bad())

        # fix the empty diff
        branch_data.raw_diff = "raw diff2"
        branch_data.has_new_commits = True
        self._process_branches([branch])
        self.assertFalse(branch.is_status_bad())

        # land ok
        self.conduit_data.accept_the_only_review()
        self._process_branches([branch])
        self.assertTrue(branch.is_null())

    def test_M_NoLandingAuthor(self):
        branch, branch_data = abdt_branchmock.create_simple_new_review()
        self._process_branches([branch])
        self.assertFalse(branch.is_status_bad())

        # set bad email addresses and accept the review
        branch_data.names_emails = abdt_branchmock.create_bad_names_emails()
        branch_data.has_new_commits = True
        self.conduit_data.accept_the_only_review()
        self._process_branches([branch])

        # ensure that the review is landed
        self.assertTrue(branch.is_null())


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
