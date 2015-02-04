"""Test suite for phlgitx_ignoreattributes."""
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
# [ C] 'Ensuring' repos with incorrect line-endings works around spurious diffs
# [ D] Can 'Ensure' a repo with supported existing content in .git/info/attr...
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_WorkaroundSpuriousIdentDiff
# [ C] test_C_WorkaroundSpuriousEolDiff
# [ D] test_D_UpdateInfoAttributes
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
import itertools
import os
import unittest

import phlgitu_fixture
import phlsys_fs
import phlsys_subprocess

import phlgitx_ignoreattributes


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        with phlgitu_fixture.lone_worker_context() as worker:

            self.assertFalse(
                phlgitx_ignoreattributes.is_repo_definitely_ignoring(
                    worker.repo.working_dir))

            phlgitx_ignoreattributes.ensure_repo_ignoring(
                worker.repo.working_dir)

            self.assertTrue(
                phlgitx_ignoreattributes.is_repo_definitely_ignoring(
                    worker.repo.working_dir))

            phlgitx_ignoreattributes.ensure_repo_ignoring(
                worker.repo.working_dir)

    def test_B_WorkaroundSpuriousIdentDiff(self):
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
            phlgitx_ignoreattributes.ensure_repo_ignoring(w1.repo.working_dir)

            # try to checkout back to the branch with the fix
            checkout_fix_ident()

    def test_C_WorkaroundSpuriousEolDiff(self):
        badeol_filename = 'badeol_file'
        linked_workers = phlgitu_fixture.CentralisedWithTwoWorkers()
        with contextlib.closing(linked_workers):

            w0 = linked_workers.w0
            w1 = linked_workers.w1

            badeol_path = os.path.join(w0.repo.working_dir, badeol_filename)

            # commit a bad eol file
            w0.commit_new_file(
                message='add file, bad line endings',
                relative_path=badeol_filename,
                contents='windows line ending, whoops!\r\n')

            # enable eol conversion
            w0.commit_new_file(
                message='add .gitattributes, set eol to unix',
                relative_path='.gitattributes',
                contents='* eol=lf\n')

            # checkout onto a new branch to fix the line ending
            w0.repo("checkout", "-b", "fix_badeol")
            phlsys_fs.write_text_file(badeol_path, "good ending\n")

            w0.repo('commit', '-am', 'fix {}'.format(badeol_filename))

            # push both branches back to share with 'w1'
            w0.repo('push', 'origin', 'master:master', 'fix_badeol')

            w1.repo('fetch', 'origin')
            w1.repo('checkout', 'origin/master')

            def checkout_fix_badeol():
                w1.repo('checkout', 'origin/fix_badeol')

            # An error will be raised here, as the badeol file will appear to
            # have been modified.
            self.assertRaises(
                phlsys_subprocess.CalledProcessError,
                checkout_fix_badeol)

            # work around the problem, by ignoring the badeol setting
            phlgitx_ignoreattributes.ensure_repo_ignoring(w1.repo.working_dir)

            # try to checkout back to the branch with the fix
            checkout_fix_badeol()

    def test_D_UpdateInfoAttributes(self):

        all_attributes = list(phlgitx_ignoreattributes._REPO_ATTRIBUTES_TUPLE)
        all_attributes.append("")

        all_lines = itertools.combinations(
            all_attributes,
            len(all_attributes) - 1)

        for lines in all_lines:

            content = "\n".join(lines)
            print(content)
            print("---")
            with phlgitu_fixture.lone_worker_context() as worker:

                working_dir = worker.repo.working_dir
                attributes_path = os.path.join(
                    working_dir, '.git/info/attributes')
                phlsys_fs.write_text_file(attributes_path, content)

                # should not throw
                phlgitx_ignoreattributes.ensure_repo_ignoring(
                    worker.repo.working_dir)


# -----------------------------------------------------------------------------
# Copyright (C) 2014-2015 Bloomberg Finance L.P.
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
