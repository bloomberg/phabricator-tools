"""Test suite for phlsys_tryloop."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import itertools
import unittest

import phlsys_tryloop

# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] tryLoopDelay returns the value from the supplied 'toTry' func on success
# [ B] tryLoopDelay accepts [] for 'delays' and still calls toTry once
# [ C] tryLoopDelay ignores exceptionToIgnore until delays is empty
# [ C] tryLoopDelay re-raises exceptionToIgnore when delays is empty
# [ D] exceptions not derived from exceptionToIgnore raise through tryLoopDelay
# [ E] tryLoopDelay calls 'onException' if exceptionToIgnore is intercepted
# [  ] tryLoopDelay waits 'delay' seconds between attempts
# [ F] endless_retry makes many valid increasing delays
# [ G] short_retry makes a finite amount of valid delays
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_ReturnsValue
# [ C] test_C_RetriesEachDelay
# [ D] test_D_RaiseThrough
# [ E] test_E_CallsOnException
# [ F] test_F_ValidLongIncreasingEndlessRetry
# [ G] test_G_ValidFiniteShortRetry
# =============================================================================


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        pass

    def test_B_ReturnsResult(self):
        self.assertEqual(1, phlsys_tryloop.try_loop_delay(lambda: 1, []))
        self.assertEqual("hi", phlsys_tryloop.try_loop_delay(lambda: "hi", []))

    def test_C_RetriesEachDelay(self):

        class TestException(Exception):
            pass

        counter = []

        def failer():
            counter.append(1)
            raise TestException()

        numDelays = 4
        delays = [datetime.timedelta() for _ in range(0, numDelays)]
        try:
            phlsys_tryloop.try_loop_delay(failer, delays, TestException)
        except TestException:
            pass
        else:
            raise Exception("did not receive TestException")

        self.assertEqual(1 + numDelays, len(counter))

    def test_D_RaiseThrough(self):

        class TestException(Exception):
            pass

        counter = []

        def failer():
            counter.append(1)
            raise TypeError()

        numDelays = 4
        delays = [datetime.timedelta() for _ in range(0, numDelays)]
        try:
            phlsys_tryloop.try_loop_delay(failer, delays, TestException)
        except TypeError:
            pass
        else:
            raise Exception("did not receive TypeError")

        self.assertEqual(1, len(counter))

    def test_E_CallsOnException(self):

        fail_counter = []
        on_exception_counter = []

        class TestException(Exception):
            pass

        def failer():
            fail_counter.append(1)
            raise TestException()

        def on_exception(e, delay):
            print(e)
            if delay is not None:
                print(delay.total_seconds())
            on_exception_counter.append(1)

        numDelays = 4
        delays = [datetime.timedelta() for _ in range(0, numDelays)]
        try:
            phlsys_tryloop.try_loop_delay(
                failer, delays, onException=on_exception)
        except TestException:
            pass
        else:
            raise Exception("did not receive TestException")

        self.assertEqual(1 + numDelays, len(fail_counter))
        self.assertEqual(len(fail_counter), len(on_exception_counter))

    def test_F_ValidLongIncreasingEndlessRetry(self):
        # [ F] endless_retry makes many valid increasing delays
        delays = phlsys_tryloop.make_default_endless_retry()

        first_secs = None
        last_secs = None
        for i in itertools.islice(delays, 1000):
            secs = i.total_seconds()
            self.assertGreaterEqual(secs, 0)
            self.assertTrue(last_secs is None or secs >= last_secs)
            if first_secs is None:
                first_secs = secs
            last_secs = secs

        self.assertGreater(last_secs, first_secs)

    def test_G_ValidFiniteShortRetry(self):
        # [ G] short_retry makes a finite amount of valid delays
        is_empty = True
        for i in phlsys_tryloop.make_default_short_retry():
            is_empty = False
            secs = i.total_seconds()
            self.assertGreaterEqual(secs, 0)
            self.assertLess(secs, 3600)  # one hour is definitely not short
        self.assertFalse(is_empty)


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
