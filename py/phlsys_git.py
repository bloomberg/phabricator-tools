"""Wrapper to call git, with working directory"""

import os
import unittest

import phlsys_subprocess

#TODO: add support for user.name and user.email to git clone


class GitClone():

    def __init__(self, workingDir):
        self._workingDir = os.path.abspath(workingDir)

    #def call(*args, stdin=None): <-- supported in Python 3
    def call(self, *args, **kwargs):
        stdin = kwargs.pop("stdin", None)
        assert(not kwargs)
        result = phlsys_subprocess.run(
            'git', *args,
            stdin=stdin, workingDir=self._workingDir)
        return result.stdout


class TestGitClone(unittest.TestCase):

    def testCanCommit(self):
        # TODO: make this more portable with shutil etc.
        run = phlsys_subprocess.run
        runCommands = phlsys_subprocess.runCommands
        path = "phlsys_git_TestGitContext"
        runCommands("mkdir " + path)
        run("git", "init", workingDir=path)
        clone = GitClone(path)
        runCommands("touch " + path + "/README")
        clone.call("add", "README")
        clone.call("commit", "-m", "initial commit")
        runCommands("rm -rf " + path)


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
