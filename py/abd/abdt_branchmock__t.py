"""Test suite for abdt_branchmock."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import phlsys_compiface

import abdt_branch
import abdt_branchmock
import abdt_branchtester

# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] public interface of mock matches abdt_branch.Branch
# [XB] can test is_abandoned, is_null, is_new
# [XC] can move between all states without error
# [XD] can set and retrieve repo name, branch link
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_InterfaceMatchesRealBranch
# [XB] test_XB_UntrackedBranch
# [XC] test_XC_MoveBetweenAllMarkedStates
# [XD] check_XD_SetRetrieveRepoNameBranchLink
# =============================================================================


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        abdt_branchmock.create_simple_new_review()

    def test_B_InterfaceMatchesRealBranch(self):
        self.assertTrue(
            phlsys_compiface.check_public_ifaces_match(
                abdt_branch.Branch,
                abdt_branchmock.BranchMock))

    def test_XB_UntrackedBranch(self):
        abdt_branchtester.check_XB_UntrackedBranch(self)

    def test_XC_MoveBetweenAllMarkedStates(self):
        abdt_branchtester.check_XC_MoveBetweenAllMarkedStates(self)

    def check_XD_SetRetrieveRepoNameBranchLink(self):
        abdt_branchtester.check_XD_SetRetrieveRepoNameBranchLink(self)

    def _setup_for_untracked_branch(self, repo_name='name', branch_url=None):
        branch, data = abdt_branchmock.create_simple_new_review(
            repo_name, branch_url)
        return data.base_branch, data.review_branch, branch


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
