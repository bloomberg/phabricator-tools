"""Test suite for abdt_branch."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [XB] can test is_abandoned, is_null, is_new
# [XC] can move between all states without error
# [XD] can set and retrieve repo name, branch link
# [ C] can move bad_pre_review -> 'new' states without duplicating branches
# [ D] unique names and emails are returned in the order of most recent first
# [  ] can detect if review branch has new commits (after ff, merge, rebase)
# [  ] can get raw diff from branch
# [  ] can get author names and emails from branch
# [  ] raise if get author names and emails from branch with no history
# [  ] raise if get author names and emails from branch with invalid base
# [  ] can 'get_any_author_emails', raise if no emails ever
# [  ] bad unicode chars in diffs
# [  ] bad unicode chars in commit messages
# [  ] can land an uncomplicated review
# [  ] XXX: withReservedBranch
# [  ] XXX: emptyMergeWorkflow
# [  ] XXX: mergeConflictWorkflow
# [  ] XXX: changeAlreadyMergedOnBase
# [  ] XXX: commandeeredLand
# [  ] XXX: createHugeReview
# [  ] XXX: hugeUpdateToReview
# [  ] XXX: empty repository, no history
# [  ] XXX: landing when origin has been updated underneath us
# [  ] XXX: moving tracker branches when there's something in the way
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_Empty
# [ C] test_C_BadPreReviewToNew
# [ D] test_D_AlternatingAuthors
# [XB] test_XB_UntrackedBranch
# [XC] test_XC_MoveBetweenAllMarkedStates
# [XD] check_XD_SetRetrieveRepoNameBranchLink
# =============================================================================

from __future__ import absolute_import

import os
import unittest

import phlgit_branch
import phlgit_push
import phlgit_revparse
import phlgitu_fixture
import phlgitx_refcache

import abdt_branch
import abdt_branchtester
import abdt_classicnaming
import abdt_git
import abdt_naming


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.repos = None
        self.repo_central = None
        self.repo_dev = None
        self.repo_arcyd = None

    def setUp(self):
        self.repos = phlgitu_fixture.CentralisedWithTwoWorkers()
        self.repo_central = self.repos.central_repo
        self.repo_dev = self.repos.w0.repo
        sys_repo = self.repos.w1.repo
        refcache_repo = phlgitx_refcache.Repo(sys_repo)
        self.repo_arcyd = abdt_git.Repo(refcache_repo, 'origin', 'myrepo')

    def tearDown(self):
        self.repos.close()

    def test_A_Breathing(self):
        pass

    def test_B_Empty(self):
        pass

    def test_C_BadPreReviewToNew(self):
        # can move bad_pre_review -> 'new' states without duplicating branches
        base, branch_name, branch = self._setup_for_untracked_branch()

        transition_list = [
            branch.mark_ok_new_review, branch.mark_new_bad_in_review
        ]

        for do_transition in transition_list:
            branches = phlgit_branch.get_remote(self.repo_arcyd, 'origin')
            branch.mark_bad_pre_review()
            branches_bad_pre = phlgit_branch.get_remote(
                self.repo_arcyd, 'origin')
            do_transition(102)
            branches_new = phlgit_branch.get_remote(self.repo_arcyd, 'origin')

            # we expect to have gained one branch when starting to track as
            # 'bad_pre_review'.
            self.assertEqual(len(branches_bad_pre), len(branches) + 1)

            # we expect to have the same number of branches after moving with
            # 'mark_ok_new_review'
            self.assertEqual(len(branches_bad_pre), len(branches_new))

            # remove the tracking branch and make sure the count has gone down
            branch.clear_mark()
            branches_cleared = phlgit_branch.get_remote(
                self.repo_arcyd, 'origin')
            self.assertEqual(len(branches_cleared), len(branches))

    def test_D_AlternatingAuthors(self):
        base, branch_name, branch = self._setup_for_untracked_branch()

        alice_user = 'Alice'
        alice_email = 'alice@server.test'

        bob_user = 'Bob'
        bob_email = 'bob@server.test'

        self._dev_commit_new_empty_file('ALICE1', alice_user, alice_email)
        self._dev_commit_new_empty_file('BOB1', bob_user, bob_email)
        self._dev_commit_new_empty_file('ALICE2', alice_user, alice_email)

        phlgit_push.push(self.repo_dev, branch_name, 'origin')
        self.repo_arcyd('fetch', 'origin')

        author_names_emails = branch.get_author_names_emails()

        self.assertTupleEqual(
            author_names_emails[0],
            (bob_user, bob_email))

        self.assertTupleEqual(
            author_names_emails[1],
            (alice_user, alice_email))

#         any_author_emails = branch.get_any_author_emails()
#         self.assertEqual(any_author_emails[-1], alice_email)
#         self.assertEqual(any_author_emails[-2], bob_email)

    def _dev_commit_new_empty_file(self, filename, user, email):
        self._create_new_file(self.repo_dev, filename)
        self.repo_dev('add', filename)
        self.repo_dev(
            'commit',
            '-m',
            filename,
            '--author=' + '{} <{}>'.format(user, email))

    def test_XB_UntrackedBranch(self):
        abdt_branchtester.check_XB_UntrackedBranch(self)

    def test_XC_MoveBetweenAllMarkedStates(self):
        abdt_branchtester.check_XC_MoveBetweenAllMarkedStates(self)

    def check_D_SetRetrieveRepoNameBranchLink(self):
        abdt_branchtester.check_XD_SetRetrieveRepoNameBranchLink(self)

    def _create_new_file(self, repo, filename):
        self.assertFalse(os.path.isfile(filename))
        open(os.path.join(repo.working_dir, filename), 'a').close()

    def _setup_for_tracked_branch(self):
        base, branch_name, branch = self._setup_for_untracked_branch()
        branch.mark_ok_new_review(101)
        return base, branch_name, branch

    def _setup_for_untracked_branch(self, repo_name='name', branch_url=None):
        base = abdt_naming.EXAMPLE_REVIEW_BRANCH_BASE

        naming = abdt_classicnaming.Naming()

        branch_name = abdt_classicnaming.EXAMPLE_REVIEW_BRANCH_NAME
        self.repo_dev('checkout', '-b', branch_name)
        phlgit_push.push(self.repo_dev, branch_name, 'origin')

        self.repo_arcyd('fetch', 'origin')

        review_branch = naming.make_review_branch_from_name(branch_name)
        review_hash = phlgit_revparse.get_sha1_or_none(
            self.repo_arcyd, review_branch.branch)

        branch = abdt_branch.Branch(
            self.repo_arcyd,
            review_branch,
            review_hash,
            None,
            None,
            None,
            repo_name,
            branch_url)

        # should not raise
        branch.verify_review_branch_base()

        return base, branch_name, branch

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
