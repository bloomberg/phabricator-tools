"""Wrapper around 'git diff'"""

import os
import re
import unittest

import phlsys_git
import phlsys_subprocess


def rawDiffRangeToHere(clone, start):
    return clone.call("diff", start + "...")


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

    def setUp(self):
        # TODO: make this more portable with shutil etc.
        self.run = phlsys_subprocess.run
        self.runCommands = phlsys_subprocess.runCommands
        self.path = "phlgit_diff_TestDiff"
        self.runCommands("mkdir " + self.path)
        self.run("git", "init", workingDir=self.path)
        self.clone = phlsys_git.GitClone(self.path)

    def _createCommitNewFile(self, filename):
        self.runCommands("touch " + os.path.join(self.path, filename))
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
        self.assertEqual(
            set(["ONLY_FORK", "ONLY_FORK2"]),
            parseFilenamesFromRawDiff(rawDiff))

    def tearDown(self):
        self.runCommands("rm -rf " + self.path)


if __name__ == "__main__":
    unittest.main()

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
