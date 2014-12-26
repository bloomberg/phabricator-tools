"""Test suite for phlsys_namedtuple."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import warnings

import phlsys_namedtuple

# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# In the interests of brevity, we'll refer to
# 'phlsys_namedtuple.make_named_tuple()' as 'make()' from here on in.
#
# In the interests of further brevity, we'll refer to functions returned by
# make() collectively as factory() from here on in.
#
# Concerns:
# [ A] factory() returns a seemingly regular namedtuple
# [ B] factory() raises a phlsys_namedtuple.Error if 'required' contains
#      items which weren't supplied to factory().
# [ D] factory() ignores parameters mentioned in 'ignored' without event
# [ C] factory() ignores parameters not mentioned in 'required', 'defaults'
#      and 'ignored', a warnings.warn is emitted if any encountered.
# [ E] make() asserts if 'required', 'default' and 'ignored' are not disjoint
# [ F] subsequent calls to make() don't affect previously created factories
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_RaiseMissing
# [ C] test_C_WarnUnexpected
# [ D] test_D_ignoreIgnored
# [ E] test_E_AssertDisjoint
# [ F] test_F_IndependentFactory
# =============================================================================


class Test(unittest.TestCase):

    def __init__(self, data):
        self.factory = None
        super(Test, self).__init__(data)

    def setUp(self):
        self.factory = phlsys_namedtuple.make_named_tuple(
            'T',
            required=['r1', 'r2'],
            defaults={'d1': 1, 'd2': 2},
            ignored=['i1', 'i2'])

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        t = self.factory(r1=1, r2=2)
        self.assertEqual(t.r1, 1)
        self.assertEqual(t.r2, 2)
        self.assertEqual(t.d1, 1)
        self.assertEqual(t.d2, 2)

    def test_B_RaiseMissing(self):
        with self.assertRaises(phlsys_namedtuple.Error):
            self.factory(r1=1)
        with self.assertRaises(phlsys_namedtuple.Error):
            self.factory(r2=2)
        with self.assertRaises(phlsys_namedtuple.Error):
            self.factory()
        with self.assertRaises(phlsys_namedtuple.Error):
            self.factory(d1=1)
        with self.assertRaises(phlsys_namedtuple.Error):
            self.factory(d2=2)

    def test_C_WarnUnexpected(self):
        # Cause all warnings to always be triggered.
        warnings.simplefilter("always")

        with warnings.catch_warnings(record=True) as w:
            self.factory(r1=1, r2=2, dingbat=3)
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "ignoring unexpected args" in str(w[-1].message)
            assert "dingbat" in str(w[-1].message)

        with warnings.catch_warnings(record=True) as w:
            self.factory(r1=1, r2=2, dingbat=3, d1=2, d2=3)
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "ignoring unexpected args" in str(w[-1].message)
            assert "dingbat" in str(w[-1].message)

        with warnings.catch_warnings(record=True) as w:
            self.factory(r1=1, r2=2, dingbat=3, d1=2, d2=3, i1=-1, i2=-2)
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "ignoring unexpected args" in str(w[-1].message)
            assert "dingbat" in str(w[-1].message)

    def test_D_IgnoreIgnored(self):
        self.factory(r1=1, r2=2, i1=-1)
        self.factory(r1=1, r2=2, i2=1)
        self.factory(r1=1, r2=2, i1=1, i2=1)

    def test_E_AssertDisjoint(self):
        with self.assertRaises(AssertionError):
            phlsys_namedtuple.make_named_tuple(
                'T',
                required=['r1', 'r2'],
                defaults={'r1': 1, 'd2': 2},
                ignored=['i1', 'i2'])
        with self.assertRaises(AssertionError):
            phlsys_namedtuple.make_named_tuple(
                'T',
                required=['r1', 'r2'],
                defaults={'d1': 1, 'd2': 2},
                ignored=['r1', 'i2'])
        with self.assertRaises(AssertionError):
            phlsys_namedtuple.make_named_tuple(
                'T',
                required=['r1', 'r2'],
                defaults={'d1': 1, 'd2': 2},
                ignored=['d1', 'i2'])
        with self.assertRaises(AssertionError):
            phlsys_namedtuple.make_named_tuple(
                'T',
                required=['a', 'r2'],
                defaults={'a': 1, 'd2': 2},
                ignored=['a', 'i2'])

    def test_F_IndependentFactory(self):
        factory1 = phlsys_namedtuple.make_named_tuple('T1', [], {}, [])
        phlsys_namedtuple.make_named_tuple('T2', [], {}, [])
        self.assertEqual(type(factory1()).__name__, 'T1')

        phlsys_namedtuple.make_named_tuple('T1', ['r1'], {}, [])
        factory1()
        phlsys_namedtuple.make_named_tuple('T1', [], {'d1': 1}, [])
        self.assertFalse(hasattr(factory1(), 'd1'))


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
