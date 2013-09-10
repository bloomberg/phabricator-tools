"""Test suite for phlsys_timedqueue."""

import datetime
import sys
import unittest

import phlsys_timedqueue

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] a default-contructed TimedQueue is empty
# [ B] an empty TimedQueue will pop_expired() []
# [  ] a TimedQueue will never try to compare the items being stored
# [ C] items are popped in the order they expire
# [ C] items expire at or after their delay
# [ C] items are only popped once
# [ E] items are not referred to after they are popped
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_DefaultConstructor
# [ C] test_C_PopOrderForward
# [ D] test_D_PopOrderBackward
# [ E] test_E_RefCountIncreaseDecrease
#==============================================================================


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        pass

    def test_B_DefaultConstructor(self):
        tq = phlsys_timedqueue.TimedQueue()
        self.assertListEqual([], tq.pop_expired())

    def test_C_PopOrderForward(self):
        tq = phlsys_timedqueue.TimedQueue()
        a = "a"
        b = "b"
        c = "c"
        no_time = datetime.timedelta()
        tq.push(a, no_time)
        tq.push(b, no_time)
        tq.push(c, no_time)
        self.assertListEqual([a, b, c], tq.pop_expired())
        self.assertListEqual([], tq.pop_expired())

    def test_D_PopOrderBackward(self):
        tq = phlsys_timedqueue.TimedQueue()
        a = "a"
        b = "b"
        c = "c"
        tq.push(a, datetime.timedelta(-1))
        tq.push(b, datetime.timedelta(-2))
        tq.push(c, datetime.timedelta(-3))
        self.assertListEqual([c, b, a], tq.pop_expired())
        self.assertListEqual([], tq.pop_expired())

    def test_E_RefCountIncreaseDecrease(self):
        tq = phlsys_timedqueue.TimedQueue()
        a = "a"
        before_count = sys.getrefcount(a)
        tq.push(a, datetime.timedelta())
        during_count = sys.getrefcount(a)
        tq.pop_expired()
        after_count = sys.getrefcount(a)

        # we expect before and after to be the same, assuming nothing external
        # is aquiring references. (e.g. the Python debugger perhaps)
        self.assertEqual(before_count, after_count)

        # we expect the count to go up whilst the TimedQueue is holding our
        # object, otherwise something must be wrong
        self.assertGreater(during_count, before_count)


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
