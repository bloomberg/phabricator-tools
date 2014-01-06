"""Test suite for phlsys_dictutil."""

from __future__ import absolute_import

import copy
import unittest

import phlsys_dictutil

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] copy_dict_no_nones() returns a dict with 'None' values stripped
# [ B] copy_dict_no_nones() returns a shallow copy of the supplied dict
# [ B] copy_dict_no_nones() does not alter the passed in dictionary
# [ C] ensure_keys() adds missing keys mapping to 'None'
# [ C] ensure_keys() does not modify existing keys
# [ D] ensure_keys_default() adds missing keys mapping to supplied 'default'
# [ D] ensure_keys_default() does not modify existing keys
# [ D] ensure_keys_default() makes a deep copy of 'default'
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_CopyDictNoNones
# [ C] test_C_EnsureKeys
# [ D] test_D_EnsureKeysDefault
#==============================================================================


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        pass

    def test_B_CopyDictNoNones(self):
        d1 = {'a': None, 'b': 1, 'c': None, 'd': None, 'e': 2, 'f': 3}
        d1copy = copy.deepcopy(d1)
        d2 = phlsys_dictutil.copy_dict_no_nones(d1)
        d3 = {'b': 1, 'e': 2, 'f': 3}
        self.assertDictEqual(d1, d1copy)
        self.assertNotEqual(d1, d2)
        self.assertDictEqual(d2, d3)

    def test_C_EnsureKeys(self):
        d1 = {'b': 1, 'e': 2, 'f': 3}
        d1copy = copy.deepcopy(d1)
        phlsys_dictutil.ensure_keys(d1, ['a', 'b', 'c', 'd', 'e'])
        self.assertDictContainsSubset(d1copy, d1)
        d2 = {'a': None, 'b': 1, 'c': None, 'd': None, 'e': 2, 'f': 3}
        self.assertDictEqual(d1, d2)

    def test_D_EnsureKeysDefault(self):
        d1 = {'b': 1, 'e': 2, 'f': 3}
        d1copy = copy.deepcopy(d1)
        default = [[0, 1, 2], 1, 2]  # nest a list to prove deep copying
        phlsys_dictutil.ensure_keys_default(
            d1, default, ['a', 'b', 'c', 'd', 'e'])
        self.assertDictContainsSubset(d1copy, d1)
        default[0][:] = []  # clear the list in place to prove we have copied
        default[:] = []  # clear the list in place to prove we have copied
        d2 = {'a': [[0, 1, 2], 1, 2],
              'b': 1,
              'c': [[0, 1, 2], 1, 2],
              'd': [[0, 1, 2], 1, 2],
              'e': 2,
              'f': 3}
        self.assertDictEqual(d1, d2)


#------------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
