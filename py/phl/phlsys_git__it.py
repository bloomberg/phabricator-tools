"""Test suite for phlsys_git."""
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
from __future__ import division
from __future__ import print_function

import unittest

import phlsys_git
import phlsys_subprocess


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_can_commit(self):
        # TODO: make this more portable with shutil etc.
        run = phlsys_subprocess.run
        runCommands = phlsys_subprocess.run_commands
        path = "phlsys_git_TestGitContext"
        runCommands("mkdir " + path)
        run("git", "init", workingDir=path)
        repo = phlsys_git.Repo(path)
        runCommands("touch " + path + "/README")
        repo("add", "README")
        repo("commit", "-m", "initial commit")
        runCommands("rm -rf " + path)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
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
