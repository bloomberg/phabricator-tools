"""Test suite for phlgit_diff."""
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

import unittest

import phlgit_diff
import phlgitu_fixture


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSimpleFork(self):
        with phlgitu_fixture.lone_worker_context() as worker:
            worker.repo("branch", "fork")
            worker.commit_new_file("add ONLY_MASTER", "ONLY_MASTER")
            worker.repo("checkout", "fork")
            worker.commit_new_file("add ONLY_FORK", "ONLY_FORK")
            worker.commit_new_file("add ONLY_FORK2", "ONLY_FORK2")
            rawDiff = phlgit_diff.raw_diff_range_to_here(
                worker.repo, "master")
            rawDiff2 = phlgit_diff.raw_diff_range(
                worker.repo, "master", "fork")
            rawDiff3 = phlgit_diff.raw_diff_range(
                worker.repo, "master", "fork", 1000)
            self.assertEqual(
                set(["ONLY_FORK", "ONLY_FORK2"]),
                phlgit_diff.parse_filenames_from_raw_diff(rawDiff))
            self.assertEqual(
                set(["ONLY_FORK", "ONLY_FORK2"]),
                phlgit_diff.parse_filenames_from_raw_diff(rawDiff2))
            self.assertEqual(
                set(["ONLY_FORK", "ONLY_FORK2"]),
                phlgit_diff.parse_filenames_from_raw_diff(rawDiff3))


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
