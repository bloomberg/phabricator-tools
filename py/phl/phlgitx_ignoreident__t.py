"""Test suite for phlgitx_ignoreident."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] New repositories report False for is_repo_definitely_ignoring()
# [ A] Can 'Ensure' new repositories with ensure_repo_ignoring()
# [ A] 'Ensured' repositories report True for is_repo_definitely_ignoring()
# [ A] Can 'Ensure' already 'Ensured' repositories without error
# [ B] 'Ensuring' repos with pre-expanded files works around spurious diffs
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_WorkaroundSpuriousDiff
# =============================================================================

from __future__ import absolute_import

import contextlib
import os
import unittest

import phlgitu_fixture
import phlsys_fs
import phlsys_subprocess

import phlgitx_ignoreident


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        with phlgitu_fixture.lone_worker_context() as worker:

            self.assertFalse(
                phlgitx_ignoreident.is_repo_definitely_ignoring(
                    worker.repo.working_dir))

            phlgitx_ignoreident.ensure_repo_ignoring(
                worker.repo.working_dir)

            self.assertTrue(
                phlgitx_ignoreident.is_repo_definitely_ignoring(
                    worker.repo.working_dir))

            phlgitx_ignoreident.ensure_repo_ignoring(
                worker.repo.working_dir)

    def test_B_WorkaroundSpuriousDiff(self):
        ident_filename = 'ident_file'
        linked_workers = phlgitu_fixture.CentralisedWithTwoWorkers()
        with contextlib.closing(linked_workers):

            w0 = linked_workers.w0
            w1 = linked_workers.w1

            ident_path = os.path.join(w0.repo.working_dir, ident_filename)

            # commit a pre-expanded file
            w0.commit_new_file(
                message='add ident, erroneously expanded already',
                relative_path=ident_filename,
                contents='$Id: already expanded, whoops! $')

            # enable ident expansion
            w0.commit_new_file(
                message='add .gitattributes, enable ident',
                relative_path='.gitattributes',
                contents='* ident\n')

            # checkout onto a new branch to fix the ident
            w0.repo("checkout", "-b", "fix_ident")
            phlsys_fs.write_text_file(ident_path, "$Id$")

            w0.repo('commit', '-am', 'fix {}'.format(ident_filename))

            # push both branches back to share with 'w1'
            w0.repo('push', 'origin', 'master:master', 'fix_ident')

            w1.repo('fetch', 'origin')
            w1.repo('checkout', 'origin/master')

            def checkout_fix_ident():
                w1.repo('checkout', 'origin/fix_ident')

            # An error will be raised here, as the ident file will appear to
            # have been modified.
            self.assertRaises(
                phlsys_subprocess.CalledProcessError,
                checkout_fix_ident)

            # work around the problem, by ignoring the ident setting
            phlgitx_ignoreident.ensure_repo_ignoring(w1.repo.working_dir)

            # try to checkout back to the branch with the fix
            checkout_fix_ident()


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
