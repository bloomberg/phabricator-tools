"""Test suite for phlmp_pool."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# TODO
# -----------------------------------------------------------------------------
# Tests:
# TODO
# =============================================================================

from __future__ import absolute_import

import multiprocessing
import unittest

import phlmp_pool


class _TestJob(object):

    def __init__(self, value):
        self._value = value

    def __call__(self):
        return self._value


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_breathing(self):
        input_list = list(xrange(100))
        job_list = [_TestJob(i) for i in input_list]
        result_list = []
        max_workers = multiprocessing.cpu_count()
        print "max_workers: ", max_workers
        for i, r in phlmp_pool.generate_results(job_list, max_workers):
            self.assertEqual(i, r)
            result_list.append(r)

        self.assertSetEqual(
            set(result_list),
            set(input_list))


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
