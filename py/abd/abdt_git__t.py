"""Test suite for abdt_git."""
#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [  ]
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
#==============================================================================

from __future__ import absolute_import

import os
import shutil
import tempfile
import unittest

import phlgit_push
import phlsys_git

import abdt_git
import abdt_rbranchnaming


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.repo_central = None
        self.repo_dev = None
        self.clone_arcyd = None

    def setUp(self):
        self.repo_central = phlsys_git.GitClone(tempfile.mkdtemp())
        self.repo_dev = phlsys_git.GitClone(tempfile.mkdtemp())
        sys_clone = phlsys_git.GitClone(tempfile.mkdtemp())
        self.clone_arcyd = abdt_git.Clone(sys_clone, 'origin', 'myrepo')

        self.repo_central.call("init", "--bare")

        self.repo_dev.call("init")
        self.repo_dev.call(
            "remote", "add", "origin", self.repo_central.working_dir)
        self.repo_dev.call("fetch")

        self._create_new_file(self.repo_dev, 'README')
        self.repo_dev.call('add', 'README')
        self.repo_dev.call('commit', '-m', 'initial commit')
        phlgit_push.push(self.repo_dev, 'master', 'origin')

        self.clone_arcyd.call("init")
        self.clone_arcyd.call(
            "remote", "add", "origin", self.repo_central.working_dir)
        self.clone_arcyd.call("fetch")

    def tearDown(self):
        shutil.rmtree(self.repo_central.working_dir)
        shutil.rmtree(self.repo_dev.working_dir)
        shutil.rmtree(self.clone_arcyd.working_dir)

    def test_A_Breathing(self):
        remote = "origin"

        expected_branches = [
            'r/master/blah',
            'r/master/blah2',
            'r/master/blah3',
        ]

        for branch in expected_branches:
            phlgit_push.push_asymmetrical(
                self.repo_dev, 'master', branch, remote)

        self.clone_arcyd.call("fetch")

        branches = abdt_git.get_managed_branches(
            self.clone_arcyd, "repo", abdt_rbranchnaming.Naming())

        actual_branches = [b.review_branch_name() for b in branches]

        self.assertSetEqual(set(expected_branches), set(actual_branches))

    def _create_new_file(self, repo, filename):
        self.assertFalse(os.path.isfile(filename))
        open(os.path.join(repo.working_dir, filename), 'a').close()


#------------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
