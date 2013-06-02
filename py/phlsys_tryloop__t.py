"""Test suite for phlsys_tryloop"""

import datetime
import unittest

import phlsys_tryloop

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_ReturnsValue
# [ C] test_C_RetriesEachDelay
# [ D] test_D_RaiseThrough
# [ E] test_E_CallsOnException
#==============================================================================


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
            print e
            if delay is not None:
                print delay.total_seconds()
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
