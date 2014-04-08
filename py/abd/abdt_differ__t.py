"""Test suite for abdt_differ."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] a diff within the limits passes straight through
# [ B] a diff outside the limits can be reduced ok with less context
# [ B] a diff still outside the limits can be reduced ok with no context
# [ C] a diff still outside the limits can be reduced to the diffstat
# [ A] raise if a diff cannot be reduced to the limits
# [  ] bad unicode chars are replaced
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_ReduceSmallChangeOnLargeFile
# [ C] test_C_ReduceAddMassiveFile
# =============================================================================

from __future__ import absolute_import

import unittest

import phlgitu_fixture

import abdt_differ
import abdt_exception


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        with phlgitu_fixture.lone_worker_context() as worker:

            worker.commit_new_file_on_new_branch(
                "diff_branch", "make a test diff", "newfile", "test content")

            def make_diff(max_bytes):
                return abdt_differ.make_raw_diff(
                    worker.repo, "master", "diff_branch", max_bytes)

            # [ A] a diff within the limits passes straight through
            diff_result = make_diff(1000)
            self.assertIn("test content", diff_result.diff)

            # [ A] raise if a diff cannot be reduced to the limits
            with self.assertRaises(abdt_exception.LargeDiffException):
                make_diff(1)

    def test_B_ReduceSmallChangeOnLargeFile(self):
        with phlgitu_fixture.lone_worker_context() as worker:

            # make a large file to base our changes on
            large_content = "lorem ipsum\n" * 1000
            worker.commit_new_file(
                "add large_file", "large_file", large_content)

            worker.append_to_file_on_new_branch(
                "diff_branch", "make small diff", "large_file", "test content")

            def make_diff(max_bytes):
                return abdt_differ.make_raw_diff(
                    worker.repo, "master", "diff_branch", max_bytes)

            # establish a baseline size for the diff
            diff_result = make_diff(100000)
            self.assertIn("test content", diff_result.diff)
            original_diff_size = len(diff_result.diff)

            # [ B] a diff outside the limits can be reduced ok with less
            #      context
            diff_result = make_diff(2000)
            self.assertIn("test content", diff_result.diff)
            reduced_context_diff_size = len(diff_result.diff)
            self.assertTrue(
                any(
                    isinstance(r, abdt_differ.LessContextReduction)
                    for r in diff_result.reduction_list))
            self.assertLess(
                reduced_context_diff_size,
                original_diff_size)

            # [ B] a diff still outside the limits can be reduced ok with no
            #      context
            diff_result = make_diff(500)
            self.assertIn("test content", diff_result.diff)
            no_context_diff_size = len(diff_result.diff)
            self.assertTrue(
                any(
                    isinstance(r, abdt_differ.RemoveContextReduction)
                    for r in diff_result.reduction_list))
            self.assertLess(
                no_context_diff_size,
                reduced_context_diff_size)

    def test_C_ReduceAddMassiveFile(self):
        with phlgitu_fixture.lone_worker_context() as worker:

            # make a large file to base our changes on
            large_content = "lorem ipsum\n" * 1000
            worker.commit_new_file_on_new_branch(
                "diff_branch", "add large_file", "large_file", large_content)

            def make_diff(max_bytes):
                return abdt_differ.make_raw_diff(
                    worker.repo, "master", "diff_branch", max_bytes)

            # establish a baseline size for the diff
            diff_result = make_diff(100000)
            self.assertIn("lorem ipsum", diff_result.diff)
            original_diff_size = len(diff_result.diff)

            # [ C] a diff still outside the limits can be reduced
            #      to the diffstat
            diff_result = make_diff(500)
            self.assertNotIn("lorem ipsum", diff_result.diff)
            diffstat_diff_size = len(diff_result.diff)
            self.assertTrue(
                any(
                    isinstance(r, abdt_differ.DiffStatReduction)
                    for r in diff_result.reduction_list))
            self.assertLess(
                diffstat_diff_size,
                original_diff_size)


# -----------------------------------------------------------------------------
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
# ------------------------------ END-OF-FILE ----------------------------------
