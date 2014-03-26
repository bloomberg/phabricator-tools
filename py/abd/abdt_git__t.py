"""Test suite for abdt_git."""
#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] changes to review branches can be detected when creating 'Branch'-es
# [ A] can create archive refs without error
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_RawDiffNewCommits
#==============================================================================

from __future__ import absolute_import

import os
import unittest

import phlgit_checkout
import phlgit_commit
import phlgit_fetch
import phlgit_merge
import phlgit_push
import phlgit_rebase
import phlgit_revparse
import phlgitu_fixture

import abdt_branch
import abdt_classicnaming
import abdt_git
import abdt_naming
import abdt_rbranchnaming


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
        self.repo_arcyd = abdt_git.Repo(sys_repo, 'origin', 'myrepo')

    def tearDown(self):
        self.repos.close()

    def test_A_Breathing(self):
        remote = "origin"

        expected_branches = [
            'r/master/blah',
            'r/master/blah2',
            'r/master/blah3',
        ]

        for branch in expected_branches:
            phlgit_push.push_asymmetrical(
                self.repo_dev, 'master', branch, remote)

        self.repo_arcyd("fetch")

        branches = abdt_git.get_managed_branches(
            self.repo_arcyd, "repo", abdt_rbranchnaming.Naming())

        actual_branches = [b.review_branch_name() for b in branches]

        self.assertSetEqual(set(expected_branches), set(actual_branches))

        for b in branches:

            self.repo_arcyd.archive_to_abandoned(
                b.review_branch_hash(),
                b.review_branch_name(),
                'master')

            self.repo_arcyd.archive_to_landed(
                b.review_branch_hash(),
                b.review_branch_name(),
                'master',
                'LANDHASH',
                'MESSAGE')

    def _get_updated_branch(self, branch_name):
        phlgit_fetch.all_prune(self.repo_arcyd)
        branch_list = abdt_git.get_managed_branches(
            self.repo_arcyd, "repo", abdt_classicnaming.Naming())
        self.assertEqual(len(branch_list), 1)
        branch = branch_list[0]
        self.assertEqual(branch.review_branch_name(), branch_name)
        return branch

    def test_B_RawDiffNewCommits(self):
        base, branch_name, branch = self._setup_for_tracked_branch()

        self.assertIs(branch.has_new_commits(), False)

        # push a new commit on branch as dev
        phlgit_checkout.branch(self.repo_dev, branch_name)
        filename = 'new_on_branch'
        self._create_new_file(self.repo_dev, filename)
        self.repo_dev('add', filename)
        phlgit_commit.index(self.repo_dev, message=filename)
        phlgit_push.branch(self.repo_dev, branch_name)

        branch = self._get_updated_branch(branch_name)

        # check for new stuff as arcyd
        self.assertIs(branch.has_new_commits(), True)
        branch.describe_new_commits()  # just exercise
        self.assertIn(filename, branch.make_raw_diff().diff)
        branch.mark_ok_in_review()
        self.assertIs(branch.has_new_commits(), False)
        branch.describe_new_commits()  # just exercise

        # exercise queries a bit
        self.assertIn(filename, branch.make_raw_diff().diff)
        self.assertIn(filename, branch.make_message_digest())
        self.assertEqual(
            branch.get_commit_message_from_tip().strip(),
            filename)
        self.assertTrue(len(branch.get_any_author_emails()) > 0)
        self.assertTrue(len(branch.get_author_names_emails()) > 0)

        # make a new commit on master as dev
        phlgit_checkout.branch(self.repo_dev, 'master')
        filename = 'new_on_master'
        self._create_new_file(self.repo_dev, filename)
        self.repo_dev('add', filename)
        phlgit_commit.index(self.repo_dev, message=filename)
        phlgit_push.branch(self.repo_dev, 'master')

        # refresh the branch
        branch = self._get_updated_branch(branch_name)
        self.assertIs(branch.has_new_commits(), False)

        # merge master into branch, check for new stuff as arcyd
        phlgit_checkout.branch(self.repo_dev, branch_name)
        phlgit_merge.no_ff(self.repo_dev, 'master')
        phlgit_push.branch(self.repo_dev, branch_name)

        # check for new stuff as arcyd
        self.assertIs(branch.has_new_commits(), False)
        branch = self._get_updated_branch(branch_name)
        self.assertNotIn(filename, branch.make_raw_diff().diff)
        branch.mark_ok_in_review()
        self.assertIs(branch.has_new_commits(), False)

        # rebase branch onto master
        phlgit_checkout.branch(self.repo_dev, branch_name)
        phlgit_rebase.onto_upstream(self.repo_dev, 'master')
        phlgit_push.force_branch(self.repo_dev, branch_name)

        # check for new stuff as arcyd
        self.assertIs(branch.has_new_commits(), False)
        branch = self._get_updated_branch(branch_name)
        self.assertIs(branch.has_new_commits(), True)
        branch.describe_new_commits()  # just exercise
        branch.mark_ok_in_review()
        self.assertIs(branch.has_new_commits(), False)

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

    def _create_new_file(self, repo, filename):
        self.assertFalse(os.path.isfile(filename))
        open(os.path.join(repo.working_dir, filename), 'a').close()


#------------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
