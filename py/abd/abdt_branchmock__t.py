"""Test suite for abdt_branchmock."""

import unittest

import phlsys_compiface

import abdt_branch
import abdt_branchmock
import abdt_branchtester

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] public interface of mock matches abdt_branch.Branch
# [XB] can test is_abandoned, is_null, is_new
# [XC] can move between all states without error
# [XD] can set and retrieve repo name, branch link
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_InterfaceMatchesRealBranch
# [XB] test_XB_UntrackedBranch
# [XC] test_XC_MoveBetweenAllMarkedStates
# [XD] check_XD_SetRetrieveRepoNameBranchLink
#==============================================================================


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
