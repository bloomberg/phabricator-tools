"""Wrapper around 'git diff'"""

import os
import re
import unittest

import phlsys_git
import phlsys_subprocess


def rawDiffRangeToHere(clone, start):
    return clone.call("diff", start + "...")


def rawDiffRange(clone, base, new, context_lines=None):
    """Return a raw diff from the history on 'new' that is not on 'base'.

    Note that commits that are cherry-picked from new to old will still appear
    in the diff, this function operates using the commit graph only.

    Raise if git returns a non-zero exit code.

    :clone: the clone to operate on
    :base: the base branch
    :new: the branch with new commits
    :returns: a string of the raw diff

    """
    if context_lines:
        result = clone.call(
            "diff", base + "..." + new, "--unified=" + str(context_lines))
    else:
        result = clone.call("diff", base + "..." + new)
    return result


def parseFilenamesFromRawDiff(diff):
    matches = re.findall(
        "^diff --git a/(.*) b/(.*)$",
        diff,
        flags=re.MULTILINE)
    if matches:
        names = zip(*matches)
        if len(names) != 2:
            raise Exception(
                "files aren't pairs in diff: " +
                diff + str(names))
        # get a set of unique names from the pairs
        unames = []
        unames.extend(names[0])
        unames.extend(names[1])
        unames = set(unames)
        return unames


class TestDiff(unittest.TestCase):

    def __init__(self, data):
        super(TestDiff, self).__init__(data)
        self.path = "phlgit_diff_TestDiff"
        self.clone = None

    def setUp(self):
        # TODO: make this more portable with shutil etc.
        phlsys_subprocess.run_commands("mkdir " + self.path)
        phlsys_subprocess.run("git", "init", workingDir=self.path)
        self.clone = phlsys_git.GitClone(self.path)

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
        rawDiff = rawDiffRangeToHere(self.clone, "master")
        rawDiff2 = rawDiffRange(self.clone, "master", "fork")
        rawDiff3 = rawDiffRange(self.clone, "master", "fork", 1000)
        self.assertEqual(
            set(["ONLY_FORK", "ONLY_FORK2"]),
            parseFilenamesFromRawDiff(rawDiff))
        self.assertEqual(
            set(["ONLY_FORK", "ONLY_FORK2"]),
            parseFilenamesFromRawDiff(rawDiff2))
        self.assertEqual(
            set(["ONLY_FORK", "ONLY_FORK2"]),
            parseFilenamesFromRawDiff(rawDiff3))

    def tearDown(self):
        phlsys_subprocess.run_commands("rm -rf " + self.path)


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
