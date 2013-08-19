"""Test suite for abdt_branchmock."""

import inspect
import unittest

import abdt_branch
import abdt_branchmock

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] public interface of mock matches abdt_branch.Branch
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_InterfaceMatchesRealConduit
#==============================================================================


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        abdt_branchmock.create_simple_new_review()

    def test_B_InterfaceMatchesRealBranch(self):
        real_interface = abdt_branch.Branch.__dict__.keys()
        real_interface = set([i for i in real_interface if i[0] != '_'])
        mock_interface = abdt_branchmock.BranchMock.__dict__.keys()
        mock_interface = set([i for i in mock_interface if i[0] != '_'])
        self.assertSetEqual(mock_interface, real_interface)

        for func_name in real_interface:
            print func_name
            real_func = abdt_branch.Branch.__dict__[func_name]
            mock_func = abdt_branchmock.BranchMock.__dict__[func_name]
            self.assertEqual(
                inspect.getargspec(real_func),
                inspect.getargspec(mock_func))


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
