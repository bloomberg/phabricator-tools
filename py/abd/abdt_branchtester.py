"""Test suite for abdt_branch-like things."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_branchtester
#
# Public Functions:
#   check_XB_UntrackedBranch
#   check_XC_MoveBetweenAllMarkedStates
#   check_XD_SetRetrieveRepoNameBranchLink
#   assert_branch_is_new
#   assert_branch_bad_pre_review
#   assert_branch_bad_in_review
#   assert_branch_bad_land
#   assert_branch_bad_abandoned
#   assert_branch_ok_in_review
#   assert_branch_is_active
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function

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
# -----------------------------------------------------------------------------
# Tests:
# [XA] XXX: check_A_Breathing
# [XB] check_XB_UntrackedBranch
# [XC] check_XC_MoveBetweenAllMarkedStates
# [XD] check_XD_SetRetrieveRepoNameBranchLink
#
# N.B. the functions begin with 'check' not 'test' so that the 'nose' test
#      runner won't try to run them for itself and fail
# =============================================================================


def check_XB_UntrackedBranch(fixture):
    base, branch_name, branch = fixture._setup_for_untracked_branch()
    assert_branch_is_new(fixture, branch, branch_name, base)


def check_XC_MoveBetweenAllMarkedStates(fixture):
    base, branch_name, branch = fixture._setup_for_untracked_branch()

    next_rev_id = [0]
    rev_id = [None]

    def ok_new_review():
        rev_id[0] = next_rev_id[0]
        next_rev_id[0] += 1
        branch.mark_ok_new_review(rev_id[0])
        assert_branch_ok_in_review(
            fixture, branch, branch_name, base, rev_id[0])

    def bad_new_in_review():
        rev_id[0] = next_rev_id[0]
        next_rev_id[0] += 1
        branch.mark_new_bad_in_review(rev_id[0])
        assert_branch_bad_in_review(
            fixture, branch, branch_name, base, rev_id[0])

    def bad_pre_review():
        rev_id[0] = None
        branch.mark_bad_pre_review()
        assert_branch_bad_pre_review(
            fixture, branch, branch_name, base)

    def bad_in_review():
        branch.mark_bad_in_review()
        assert_branch_bad_in_review(
            fixture, branch, branch_name, base, rev_id[0])

    def ok_in_review():
        branch.mark_ok_in_review()
        assert_branch_ok_in_review(
            fixture, branch, branch_name, base, rev_id[0])

    def bad_land():
        branch.mark_bad_land()
        assert_branch_bad_land(fixture, branch, branch_name, base, rev_id[0])

    def bad_abandoned():
        branch.mark_bad_abandoned()
        assert_branch_bad_abandoned(
            fixture, branch, branch_name, base, rev_id[0])

    # visit all the states reachable from bad_pre_review
    suite = {
        'initial_states': [bad_pre_review],
        'transitions': [ok_new_review, bad_new_in_review, bad_pre_review]
    }
    for initial in suite['initial_states']:
        for transition in suite['transitions']:
            print('', initial.__name__)
            print('', transition.__name__)
            initial()
            print('rev_id', branch.review_id_or_none())
            transition()
            branch.clear_mark()

    # visit all the states reachable from the initial in_review states
    # travel between each of the non-'new' in_review states
    suite = {
        'initial_states': [ok_new_review, bad_new_in_review],
        'transitions': [bad_in_review, ok_in_review, bad_land, bad_abandoned]
    }
    for initial in suite['initial_states']:
        for transition1 in suite['transitions']:
            for transition2 in suite['transitions']:
                print('', initial.__name__)
                print('', transition1.__name__)
                print('', transition2.__name__)
                initial()
                print('rev_id', branch.review_id_or_none())
                transition1()
                transition2()
                branch.clear_mark()


def check_XD_SetRetrieveRepoNameBranchLink(fixture):

    # regular case, repo name and url supplied
    repo_name = 'repo'
    browse_url = 'http://server.test/mybranch'
    base, branch_name, branch = fixture._setup_for_untracked_branch(
        repo_name, browse_url)
    fixture.assertEqual(branch.get_repo_name(), repo_name)
    fixture.assertEqual(branch.get_browse_url(), browse_url)

    # regular case, repo name and url not supplied
    repo_name = 'repo'
    browse_url = None
    base, branch_name, branch = fixture._setup_for_untracked_branch(
        repo_name, browse_url)
    fixture.assertEqual(branch.get_repo_name(), repo_name)
    fixture.assertIsNone(branch.get_browse_url())

    # error case, repo name and url not supplied
    repo_name = None
    browse_url = None
    fixture.assertRaises(
        AssertionError,
        fixture._setup_for_untracked_branch,
        repo_name, browse_url)

    # error case, repo name and url not supplied
    repo_name = None
    browse_url = None
    fixture.assertRaises(
        AssertionError,
        fixture._setup_for_untracked_branch,
        repo_name, browse_url)


def assert_branch_is_new(fixture, branch, branch_name, base):
    fixture.assertIs(branch.is_abandoned(), False)
    fixture.assertIs(branch.is_null(), False)
    fixture.assertIs(branch.is_new(), True)
    fixture.assertIs(branch.is_status_bad_pre_review(), False)
    fixture.assertIs(branch.is_status_bad_abandoned(), False)
    fixture.assertIs(branch.is_status_bad_land(), False)
    fixture.assertIs(branch.is_status_bad(), False)
    fixture.assertIs(branch.has_new_commits(), True)
    fixture.assertEqual(branch.base_branch_name(), base)
    fixture.assertEqual(branch.review_branch_name(), branch_name)
    fixture.assertIsNone(branch.review_id_or_none())
    branch.describe()  # exercise 'describe'


def assert_branch_bad_pre_review(fixture, branch, branch_name, base):
    fixture.assertIs(branch.is_status_bad_pre_review(), True)
    fixture.assertIs(branch.is_status_bad_abandoned(), False)
    fixture.assertIs(branch.is_status_bad_land(), False)
    fixture.assertIs(branch.is_status_bad(), True)
    assert_branch_is_active(fixture, branch, branch_name, base, None)


def assert_branch_bad_in_review(fixture, branch, branch_name, base, rev_id):
    fixture.assertIs(branch.is_status_bad_pre_review(), False)
    fixture.assertIs(branch.is_status_bad_abandoned(), False)
    fixture.assertIs(branch.is_status_bad_land(), False)
    fixture.assertIs(branch.is_status_bad(), True)
    assert_branch_is_active(fixture, branch, branch_name, base, rev_id)


def assert_branch_bad_land(fixture, branch, branch_name, base, rev_id):
    fixture.assertIs(branch.is_status_bad_pre_review(), False)
    fixture.assertIs(branch.is_status_bad_abandoned(), False)
    fixture.assertIs(branch.is_status_bad_land(), True)
    fixture.assertIs(branch.is_status_bad(), True)
    assert_branch_is_active(fixture, branch, branch_name, base, rev_id)


def assert_branch_bad_abandoned(fixture, branch, branch_name, base, rev_id):
    fixture.assertIs(branch.is_status_bad_pre_review(), False)
    fixture.assertIs(branch.is_status_bad_abandoned(), True)
    fixture.assertIs(branch.is_status_bad_land(), False)
    fixture.assertIs(branch.is_status_bad(), True)
    assert_branch_is_active(fixture, branch, branch_name, base, rev_id)


def assert_branch_ok_in_review(fixture, branch, branch_name, base, rev_id):
    fixture.assertIs(branch.is_status_bad_pre_review(), False)
    fixture.assertIs(branch.is_status_bad_abandoned(), False)
    fixture.assertIs(branch.is_status_bad_land(), False)
    fixture.assertIs(branch.is_status_bad(), False)
    assert_branch_is_active(fixture, branch, branch_name, base, rev_id)


def assert_branch_is_active(fixture, branch, branch_name, base, rev_id):
    fixture.assertIs(branch.is_abandoned(), False)
    fixture.assertIs(branch.is_null(), False)
    fixture.assertIs(branch.is_new(), False)
    fixture.assertEqual(branch.base_branch_name(), base)
    fixture.assertEqual(branch.review_branch_name(), branch_name)
    if rev_id is None:
        fixture.assertIsNone(branch.review_id_or_none())
    else:
        fixture.assertEqual(branch.review_id_or_none(), rev_id)
    branch.describe()  # exercise 'describe'


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
