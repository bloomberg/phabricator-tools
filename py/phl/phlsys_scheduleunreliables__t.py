"""Test suite for phlsys_scheduleunreliables"""

import datetime
import functools
import unittest

import phlsys_scheduleunreliables

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] loopOnce performs all operations
# [ C] loopOnce moves bad operations into paused_operations
# [ D] loopOnce moves expired bad operations into operations
# [ E] loopOnce drops bad operations which return 'None' from getDelay()
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_AllOperations
# [ C] test_C_MakeBadOperations
# [ D] test_D_ExpireBadOperations
# [ E] test_E_DropBadOperations
#==============================================================================


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        pass

    def test_B_AllOperations(self):
        results = set()

        def do(s):
            results.add(s)

        def makeOperation(s):
            delays = []
            return phlsys_scheduleunreliables.DelayedRetryNotifyOperation(
                functools.partial(do, s), delays)

        # make 9 operations, each just append their number to 'results'
        # N.B. loopOnce() expects a set
        data = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
        operations = set([makeOperation(i) for i in data])

        phlsys_scheduleunreliables.loopOnce(
            operations, phlsys_scheduleunreliables.makeTimedQueue())

        self.assertSetEqual(data, results)

    def test_C_MakeBadOperations(self):
        # make 10 bad operations which fail immediately
        # N.B. loopOnce() expects a set

        def bad_do():
            raise Exception("bad_do")

        def reportNothing(_):
            pass

        def makeOperation():
            delays = [datetime.timedelta()]  # expire immediately
            return phlsys_scheduleunreliables.DelayedRetryNotifyOperation(
                bad_do, delays, reportNothing)

        num_operations = 10
        operations = set([makeOperation() for _ in range(0, num_operations)])
        self.assertEqual(num_operations, len(operations))

        bad_operations = phlsys_scheduleunreliables.makeTimedQueue()
        phlsys_scheduleunreliables.loopOnce(
            operations, bad_operations)

        # loopOnce() should have moved all our operations into bad_operations
        # now we will try to extract them, as they have a delay of zero
        self.assertEqual(0, len(operations))
        expired_operations = bad_operations.pop_expired()
        self.assertEqual(num_operations, len(expired_operations))

    def test_D_ExpireBadOperations(self):
        # make 9 operations, each just append their number to 'results' and
        # then fail by raising an Exception
        # N.B. loopOnce() expects a set

        results = set()

        def bad_do(s):
            results.add(s)
            raise Exception("bad_do")

        def reportNothing(_):
            pass

        def makeOperation(s):
            delays = [datetime.timedelta()]  # expire immediately
            return phlsys_scheduleunreliables.DelayedRetryNotifyOperation(
                functools.partial(bad_do, s), delays, reportNothing)

        data = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
        operations = set([makeOperation(i) for i in data])

        bad_operations = phlsys_scheduleunreliables.makeTimedQueue()

        phlsys_scheduleunreliables.loopOnce(
            operations, bad_operations)
        self.assertSetEqual(data, results)

        # we should fill the results with the same data again
        results = set()
        phlsys_scheduleunreliables.loopOnce(
            operations, bad_operations)
        self.assertSetEqual(data, results)

    def test_E_DropBadOperations(self):
        # make 10 operations, each just fail by raising an Exception.
        # they will have no associated delay and so should not appear in
        # 'operations' or in 'bad_operations'

        num_operations = 10

        def bad_do():
            raise Exception("bad_do")

        def reportNothing(_):
            pass

        def makeOperation():
            delays = []
            return phlsys_scheduleunreliables.DelayedRetryNotifyOperation(
                functools.partial(bad_do), delays, reportNothing)

        # N.B. loopOnce() expects a set
        operations = set([makeOperation() for _ in range(0, num_operations)])
        self.assertEqual(num_operations, len(operations))

        bad_operations = phlsys_scheduleunreliables.makeTimedQueue()

        phlsys_scheduleunreliables.loopOnce(
            operations, bad_operations)
        self.assertEqual(0, len(operations))
        self.assertEqual(0, len(bad_operations.pop_expired()))


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
