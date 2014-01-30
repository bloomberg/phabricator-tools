"""Test suite for phlgit_diff."""
#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# TODO
#------------------------------------------------------------------------------
# Tests:
# TODO
#==============================================================================

from __future__ import absolute_import

import os
import unittest

import phlsys_git
import phlsys_subprocess

import phlgit_diff


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.path = "phlgit_diff_TestDiff"
        self.clone = None

    def setUp(self):
        # TODO: make this more portable with shutil etc.
        phlsys_subprocess.run_commands("mkdir " + self.path)
        phlsys_subprocess.run("git", "init", workingDir=self.path)
        self.clone = phlsys_git.Repo(self.path)

    def tearDown(self):
        phlsys_subprocess.run_commands("rm -rf " + self.path)

    def _createCommitNewFile(self, filename):
        phlsys_subprocess.run_commands(
            "touch " + os.path.join(self.path, filename))
        self.clone.call("add", filename)
        self.clone.call("commit", "-a", "-m", filename)

    def testSimpleFork(self):
        self._createCommitNewFile("README")
        self.clone.call("branch", "fork")
        self._createCommitNewFile("ONLY_MASTER")
        self.clone.call("checkout", "fork")
        self._createCommitNewFile("ONLY_FORK")
        self._createCommitNewFile("ONLY_FORK2")
        rawDiff = phlgit_diff.raw_diff_range_to_here(self.clone, "master")
        rawDiff2 = phlgit_diff.raw_diff_range(self.clone, "master", "fork")
        rawDiff3 = phlgit_diff.raw_diff_range(
            self.clone, "master", "fork", 1000)
        self.assertEqual(
            set(["ONLY_FORK", "ONLY_FORK2"]),
            phlgit_diff.parse_filenames_from_raw_diff(rawDiff))
        self.assertEqual(
            set(["ONLY_FORK", "ONLY_FORK2"]),
            phlgit_diff.parse_filenames_from_raw_diff(rawDiff2))
        self.assertEqual(
            set(["ONLY_FORK", "ONLY_FORK2"]),
            phlgit_diff.parse_filenames_from_raw_diff(rawDiff3))


#------------------------------------------------------------------------------
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
#------------------------------- END-OF-FILE ----------------------------------
