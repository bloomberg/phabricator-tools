"""Test suite for phlsys_timedqueue."""

from __future__ import absolute_import

import datetime
import sys
import unittest

import phlsys_timedqueue

# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_DefaultConstructor
# [ C] test_C_PopOrderForward
# [ D] test_D_PopOrderBackward
# [ E] test_E_RefCountIncreaseDecrease
# =============================================================================


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
