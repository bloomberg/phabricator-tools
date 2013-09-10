"""Test suite for phlsys_namedtuple."""

import unittest
import warnings

import phlsys_namedtuple

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_RaiseMissing
# [ C] test_C_WarnUnexpected
# [ D] test_D_ignoreIgnored
# [ E] test_E_AssertDisjoint
# [ F] test_F_IndependentFactory
#==============================================================================


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
