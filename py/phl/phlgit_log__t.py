"""Test suite for phlgit_log."""
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

import os
import unittest

import phlsys_git
import phlsys_subprocess

import phlgit_log


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.path = "phlgit_diff_TestDiff"
        self.repo = None
        self.authorName = "No one"
        self.authorEmail = "noone@nowhere.com"
        self.author = self.authorName + " <" + self.authorEmail + ">"

    def setUp(self):
        # TODO: make this more portable with shutil etc.
        phlsys_subprocess.run_commands("mkdir " + self.path)
        phlsys_subprocess.run("git", "init", workingDir=self.path)
        self.repo = phlsys_git.Repo(self.path)

    def tearDown(self):
        phlsys_subprocess.run_commands("rm -rf " + self.path)

    def _createCommitNewFile(self, filename, subject=None, message=None):
        phlsys_subprocess.run_commands(
            "touch " + os.path.join(self.path, filename))
        self.repo("add", filename)
        if not subject:
            if message:
                raise Exception("didn't expect message with empty subject")
            self.repo(
                "commit", "-a", "-m", filename,
                "--author", self.author)
        elif not message:
            self.repo(
                "commit", "-a", "-m", subject,
                "--author", self.author)
        else:
            message = subject + "\n\n" + message
            self.repo(
                "commit", "-a", "-m", message,
                "--author", self.author)

#     def testNoCommits(self):
#         hashes = get_range_to_here_hashes(self.repo, "HEAD")
#         self.assertIsNotNone(hashes)
#         self.assertTrue(not hashes)
#         self.assertIsInstance(hashes, list)
#         head = get_last_commit_hash(self.repo)
#         self.assertIsNone(head)
#         head2 = get_last_n_commit_hashes(self.repo, 1)
#         self.assertIsNotNone(head2)
#         self.assertEqual(head, head2[0])

    def testOneCommit(self):
        self._createCommitNewFile("README")
        hashes = phlgit_log.get_range_to_here_hashes(self.repo, "HEAD")
        self.assertIsNotNone(hashes)
        self.assertTrue(not hashes)
        self.assertIsInstance(hashes, list)
        head = phlgit_log.get_last_commit_hash(self.repo)
        self.assertIsNotNone(head)
        head2 = phlgit_log.get_last_n_commit_hashes(self.repo, 1)
        self.assertIsNotNone(head2)
        self.assertEqual(head, head2[0])
        self.assertListEqual(
            phlgit_log.get_last_n_commit_hashes(self.repo, 0), [])
        self.assertRaises(
            ValueError, phlgit_log.get_last_n_commit_hashes, self.repo, 2)

    def testTwoCommits(self):
        self._createCommitNewFile("README")
        self._createCommitNewFile("README2")
        head = phlgit_log.get_last_commit_hash(self.repo)
        self.assertIsNotNone(head)
        hashes = phlgit_log.get_last_n_commit_hashes(self.repo, 2)
        self.assertIsNotNone(hashes)
        self.assertEqual(head, hashes[-1])
        self.assertListEqual(hashes, hashes)

    def testSimpleFork(self):
        self._createCommitNewFile("README")
        self.repo("branch", "fork")
        self._createCommitNewFile("ONLY_MASTER")
        self.repo("checkout", "fork")
        self._createCommitNewFile("ONLY_FORK", "ONLY_FORK", "BODY\nBODY")
        self._createCommitNewFile("ONLY_FORK2")

        log = phlgit_log.get_range_to_here_raw_body(self.repo, "master")
        self.assertIn("ONLY_FORK", log)
        self.assertNotIn("ONLY_MASTER", log)
        self.assertNotIn("README", log)

        hashes = phlgit_log.get_range_to_here_hashes(self.repo, "master")
        hashes2 = phlgit_log.get_range_hashes(self.repo, "master", "fork")
        self.assertListEqual(hashes, hashes2)
        r0 = phlgit_log.make_revision_from_hash(self.repo, hashes[0])
        self.assertEqual(r0.subject, "ONLY_FORK")
        self.assertEqual(r0.message, "BODY\nBODY\n")
        r1 = phlgit_log.make_revision_from_hash(self.repo, hashes[1])
        self.assertEqual(r1.subject, "ONLY_FORK2")
        self.assertIsNotNone(r1.message)
        self.assertIsInstance(r1.message, str)

        committers = phlgit_log.get_author_names_emails_from_hashes(
            self.repo, hashes)
        self.assertEqual(len(committers), 1)
        self.assertEqual(committers[0], (self.authorName, self.authorEmail))


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
