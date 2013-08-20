"""Test suite for abdt_branch-like things."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_branchtester
#
# Public Functions:
#   check_B_UntrackedBranch
#   check_C_MoveBetweenAllMarkedStates
#   check_D_RawDiffNewCommits
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

# TODO: no git deps
import phlgit_checkout
import phlgit_commit
import phlgit_fetch
import phlgit_merge
import phlgit_push
import phlgit_rebase

import abdt_branch
import abdt_gittypes
import abdt_naming


#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] can test is_abandoned, is_null, is_new
# [ C] can move between all states without error
# [  ] can detect if review branch has new commits (after ff, merge, rebase)
# [  ] can get raw diff from branch
# [  ] can get author names and emails from branch
# [  ] raise if get author names and emails from branch with no history
# [  ] raise if get author names and emails from branch with invalid base
# [  ] can 'get_any_author_emails', raise if no emails ever
# [  ] bad unicode chars in diffs
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
# [ A] XXX: check_A_Breathing
# [ B] check_B_UntrackedBranch
# [ C] check_C_MoveBetweenAllMarkedStates
# [ D] check_D_RawDiffNewCommits
#
# N.B. the functions begin with 'check' not 'test' so that the 'nose' test
#      runner won't try to run them for itself and fail
#==============================================================================


def _setup_for_untracked_branch(fixture):
    fixture._create_new_file(fixture.repo_dev, 'README')
    fixture.repo_dev.call('add', 'README')
    fixture.repo_dev.call('commit', '-m', 'initial commit')
    phlgit_push.push(fixture.repo_dev, 'master', 'origin')

    base = 'master'
    description = 'untracked'

    branch_name = abdt_naming.makeReviewBranchName(description, base)
    fixture.repo_dev.call('checkout', '-b', branch_name)
    phlgit_push.push(fixture.repo_dev, branch_name, 'origin')

    fixture.clone_arcyd.call('fetch', 'origin')
    review_branch = abdt_naming.makeReviewBranchFromName(branch_name)
    review_branch = abdt_gittypes.makeGitReviewBranch(
        review_branch, 'origin')
    branch = abdt_branch.Branch(
        fixture.clone_arcyd, review_branch, None, None)

    fixture._assert_branch_is_new(branch, branch_name, base)

    # should not raise
    branch.verify_review_branch_base()

    return base, branch_name, branch


def check_B_UntrackedBranch(fixture):
    base, branch_name, branch = _setup_for_untracked_branch(fixture)


def check_C_MoveBetweenAllMarkedStates(fixture):
    base, branch_name, branch = _setup_for_untracked_branch(fixture)

    next_rev_id = [0]
    rev_id = [None]

    def ok_new_review():
        rev_id[0] = next_rev_id[0]
        next_rev_id[0] += 1
        branch.mark_ok_new_review(rev_id[0])
        fixture._assert_branch_ok_in_review(
            branch, branch_name, base, rev_id[0])

    def bad_new_in_review():
        rev_id[0] = next_rev_id[0]
        next_rev_id[0] += 1
        branch.mark_new_bad_in_review(rev_id[0])
        fixture._assert_branch_bad_in_review(
            branch, branch_name, base, rev_id[0])

    def bad_pre_review():
        rev_id[0] = None
        branch.mark_bad_pre_review()
        fixture._assert_branch_bad_pre_review(
            branch, branch_name, base, rev_id[0])

    def bad_in_review():
        branch.mark_bad_in_review()
        fixture._assert_branch_bad_in_review(
            branch, branch_name, base, rev_id[0])

    def ok_in_review():
        branch.mark_ok_in_review()
        fixture._assert_branch_ok_in_review(
            branch, branch_name, base, rev_id[0])

    def bad_land():
        branch.mark_bad_land()
        fixture._assert_branch_bad_land(branch, branch_name, base, rev_id[0])

    initial_states = [ok_new_review, bad_new_in_review, bad_pre_review]
    transitions = [bad_in_review, ok_in_review, bad_land]

    for initial in initial_states:
        for transition1 in transitions:
            for transition2 in transitions:
                initial()
                print rev_id[0]
                transition1()
                transition2()
                # print '', initial.__name__
                # print '', transition1.__name__
                # print '', transition2.__name__


def check_D_RawDiffNewCommits(fixture):
    base, branch_name, branch = fixture._setup_for_tracked_branch()

    # push a new commit on branch as dev
    phlgit_checkout.branch(fixture.repo_dev, branch_name)
    filename = 'new_on_branch'
    fixture._create_new_file(fixture.repo_dev, filename)
    fixture.repo_dev.call('add', filename)
    phlgit_commit.index(fixture.repo_dev, message=filename)
    phlgit_push.branch(fixture.repo_dev, branch_name)

    # check for new stuff as arcyd
    fixture.assertIs(branch.has_new_commits(), False)
    phlgit_fetch.all_prune(fixture.clone_arcyd)
    fixture.assertIs(branch.has_new_commits(), True)
    fixture.assertIn(filename, branch.make_raw_diff())
    branch.mark_ok_in_review()
    fixture.assertIs(branch.has_new_commits(), False)

    # exercise queries a bit
    fixture.assertIn(filename, branch.make_raw_diff())
    fixture.assertIn(filename, branch.make_message_digest())
    fixture.assertEqual(
        branch.get_commit_message_from_tip().strip(),
        filename)
    fixture.assertTrue(len(branch.get_any_author_emails()) > 0)
    fixture.assertTrue(len(branch.get_author_names_emails()) > 0)

    # check for new stuff as arcyd again
    phlgit_fetch.all_prune(fixture.clone_arcyd)
    fixture.assertIs(branch.has_new_commits(), False)

    # make a new commit on master as dev
    phlgit_checkout.branch(fixture.repo_dev, 'master')
    filename = 'new_on_master'
    fixture._create_new_file(fixture.repo_dev, filename)
    fixture.repo_dev.call('add', filename)
    phlgit_commit.index(fixture.repo_dev, message=filename)
    phlgit_push.branch(fixture.repo_dev, 'master')

    # check for new stuff as arcyd
    phlgit_fetch.all_prune(fixture.clone_arcyd)
    fixture.assertIs(branch.has_new_commits(), False)

    # merge master into branch, check for new stuff as arcyd
    phlgit_checkout.branch(fixture.repo_dev, branch_name)
    phlgit_merge.no_ff(fixture.repo_dev, 'master')
    phlgit_push.branch(fixture.repo_dev, branch_name)

    # check for new stuff as arcyd
    fixture.assertIs(branch.has_new_commits(), False)
    phlgit_fetch.all_prune(fixture.clone_arcyd)
    fixture.assertNotIn(filename, branch.make_raw_diff())
    branch.mark_ok_in_review()
    fixture.assertIs(branch.has_new_commits(), False)

    # rebase branch onto master
    phlgit_checkout.branch(fixture.repo_dev, branch_name)
    phlgit_rebase.onto_upstream(fixture.repo_dev, 'master')
    phlgit_push.force_branch(fixture.repo_dev, branch_name)

    # check for new stuff as arcyd
    fixture.assertIs(branch.has_new_commits(), False)
    phlgit_fetch.all_prune(fixture.clone_arcyd)
    fixture.assertIs(branch.has_new_commits(), True)
    branch.mark_ok_in_review()
    fixture.assertIs(branch.has_new_commits(), False)


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
