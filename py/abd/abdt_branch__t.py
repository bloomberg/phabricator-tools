"""Test suite for abdt_branch."""
#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [XB] can test is_abandoned, is_null, is_new
# [XC] can move between all states without error
# [XD] can set and retrieve repo name, branch link
# [ C] can move bad_pre_review -> 'new' states without duplicating branches
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
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_RawDiffNewCommits
# [XB] test_XB_UntrackedBranch
# [XC] test_XC_MoveBetweenAllMarkedStates
# [XD] check_XD_SetRetrieveRepoNameBranchLink
# [ C] test_C_BadPreReviewToNew
#==============================================================================

from __future__ import absolute_import

import os
import shutil
import tempfile
import unittest

import phlgit_branch
import phlgit_checkout
import phlgit_commit
import phlgit_fetch
import phlgit_merge
import phlgit_push
import phlgit_rebase
import phlsys_git

import abdt_branch
import abdt_branchtester
import abdt_git
import abdt_gittypes
import abdt_naming


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.repo_central = None
        self.repo_dev = None
        self.clone_arcyd = None

    def setUp(self):
        self.repo_central = phlsys_git.GitClone(tempfile.mkdtemp())
        self.repo_dev = phlsys_git.GitClone(tempfile.mkdtemp())
        sys_clone = phlsys_git.GitClone(tempfile.mkdtemp())
        self.clone_arcyd = abdt_git.Clone(
            sys_clone, 'origin', "myrepo", "http://git/{branch}")

        self.repo_central.call("init", "--bare")

        self.repo_dev.call("init")
        self.repo_dev.call(
            "remote", "add", "origin", self.repo_central.working_dir)

        self.clone_arcyd.call("init")
        self.clone_arcyd.call(
            "remote", "add", "origin", self.repo_central.working_dir)

    def test_A_Breathing(self):
        pass

    def test_B_RawDiffNewCommits(self):
        base, branch_name, branch = self._setup_for_tracked_branch()

        # push a new commit on branch as dev
        phlgit_checkout.branch(self.repo_dev, branch_name)
        filename = 'new_on_branch'
        self._create_new_file(self.repo_dev, filename)
        self.repo_dev.call('add', filename)
        phlgit_commit.index(self.repo_dev, message=filename)
        phlgit_push.branch(self.repo_dev, branch_name)

        # check for new stuff as arcyd
        self.assertIs(branch.has_new_commits(), False)
        phlgit_fetch.all_prune(self.clone_arcyd)
        self.assertIs(branch.has_new_commits(), True)
        self.assertIn(filename, branch.make_raw_diff())
        branch.mark_ok_in_review()
        self.assertIs(branch.has_new_commits(), False)

        # exercise queries a bit
        self.assertIn(filename, branch.make_raw_diff())
        self.assertIn(filename, branch.make_message_digest())
        self.assertEqual(
            branch.get_commit_message_from_tip().strip(),
            filename)
        self.assertTrue(len(branch.get_any_author_emails()) > 0)
        self.assertTrue(len(branch.get_author_names_emails()) > 0)

        # check for new stuff as arcyd again
        phlgit_fetch.all_prune(self.clone_arcyd)
        self.assertIs(branch.has_new_commits(), False)

        # make a new commit on master as dev
        phlgit_checkout.branch(self.repo_dev, 'master')
        filename = 'new_on_master'
        self._create_new_file(self.repo_dev, filename)
        self.repo_dev.call('add', filename)
        phlgit_commit.index(self.repo_dev, message=filename)
        phlgit_push.branch(self.repo_dev, 'master')

        # check for new stuff as arcyd
        phlgit_fetch.all_prune(self.clone_arcyd)
        self.assertIs(branch.has_new_commits(), False)

        # merge master into branch, check for new stuff as arcyd
        phlgit_checkout.branch(self.repo_dev, branch_name)
        phlgit_merge.no_ff(self.repo_dev, 'master')
        phlgit_push.branch(self.repo_dev, branch_name)

        # check for new stuff as arcyd
        self.assertIs(branch.has_new_commits(), False)
        phlgit_fetch.all_prune(self.clone_arcyd)
        self.assertNotIn(filename, branch.make_raw_diff())
        branch.mark_ok_in_review()
        self.assertIs(branch.has_new_commits(), False)

        # rebase branch onto master
        phlgit_checkout.branch(self.repo_dev, branch_name)
        phlgit_rebase.onto_upstream(self.repo_dev, 'master')
        phlgit_push.force_branch(self.repo_dev, branch_name)

        # check for new stuff as arcyd
        self.assertIs(branch.has_new_commits(), False)
        phlgit_fetch.all_prune(self.clone_arcyd)
        self.assertIs(branch.has_new_commits(), True)
        branch.mark_ok_in_review()
        self.assertIs(branch.has_new_commits(), False)

    def test_C_BadPreReviewToNew(self):
        # can move bad_pre_review -> 'new' states without duplicating branches
        base, branch_name, branch = self._setup_for_untracked_branch()

        transition_list = [
            branch.mark_ok_new_review, branch.mark_new_bad_in_review
        ]

        for do_transition in transition_list:
            branches = phlgit_branch.get_remote(self.clone_arcyd, 'origin')
            branch.mark_bad_pre_review()
            branches_bad_pre = phlgit_branch.get_remote(
                self.clone_arcyd, 'origin')
            do_transition(102)
            branches_new = phlgit_branch.get_remote(self.clone_arcyd, 'origin')

            # we expect to have gained one branch when starting to track as
            # 'bad_pre_review'.
            self.assertEqual(len(branches_bad_pre), len(branches) + 1)

            # we expect to have the same number of branches after moving with
            # 'mark_ok_new_review'
            self.assertEqual(len(branches_bad_pre), len(branches_new))

            # remove the tracking branch and make sure the count has gone down
            branch.clear_mark()
            branches_cleared = phlgit_branch.get_remote(
                self.clone_arcyd, 'origin')
            self.assertEqual(len(branches_cleared), len(branches))

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
        self._create_new_file(self.repo_dev, 'README')
        self.repo_dev.call('add', 'README')
        self.repo_dev.call('commit', '-m', 'initial commit')
        phlgit_push.push(self.repo_dev, 'master', 'origin')

        base = 'master'
        description = 'untracked'

        branch_name = abdt_naming.makeReviewBranchName(description, base)
        self.repo_dev.call('checkout', '-b', branch_name)
        phlgit_push.push(self.repo_dev, branch_name, 'origin')

        self.clone_arcyd.call('fetch', 'origin')
        review_branch = abdt_naming.makeReviewBranchFromName(branch_name)
        review_branch = abdt_gittypes.makeGitReviewBranch(
            review_branch, 'origin')
        branch = abdt_branch.Branch(
            self.clone_arcyd,
            review_branch,
            None,
            None,
            repo_name,
            branch_url)

        # should not raise
        branch.verify_review_branch_base()

        return base, branch_name, branch

    def tearDown(self):
        shutil.rmtree(self.repo_central.working_dir)
        shutil.rmtree(self.repo_dev.working_dir)
        shutil.rmtree(self.clone_arcyd.working_dir)

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
