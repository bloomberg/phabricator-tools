"""Test suite for atet_arcyd_instance."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] daemon is not started by default
# [ A] daemon is started within daemon_context
# [ A] daemon is stopped outside daemon_context
# [ B] overrun secs are not set by default
# [ B] overrun secs are set by set_overrun_secs
# [ B] set_overrun_secs writes correct value to config
# [ C] count_cycles is disabled by default
# [ C] count_cycles is enabled by enable_count_cycles_script
# [ C] correct number of cycles counted - 3 (2 + 1)
# [ D] info_log returns correct info log
# [ D] debug_log returns correct debug log
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_exercise_daemon
# [ B] test_B_exercise_overrun_secs
# [ C] test_C_exercise_wait_cycles
# [ D] test_D_exercise_read_log
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
import os
import unittest

import phldef_conduit
import phlsys_fs

import atet_fixture


@contextlib.contextmanager
def setup_arcyd():
    def make_creds_from_account(account):
        return (
            account.user,
            account.email,
            account.certificate,
        )

    script_dir = os.path.dirname(os.path.realpath(__file__))
    py_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(py_dir)
    arcyd_cmd_path = os.path.join(
        root_dir, 'testbed', 'arcyd-tester', 'git_fetch_counter_arcyd.py')
    barc_cmd_path = os.path.join(root_dir, 'proto', 'barc')
    arcyon_cmd_path = os.path.join(root_dir, 'bin', 'arcyon')
    phab_uri = phldef_conduit.TEST_URI
    arcyd_user, arcyd_email, arcyd_cert = make_creds_from_account(
        phldef_conduit.PHAB)

    arcyd_count = 1
    repo_count = 1
    fixture = atet_fixture.Fixture(
        arcyd_cmd_path,
        barc_cmd_path,
        arcyon_cmd_path,
        phab_uri,
        repo_count,
        arcyd_count,
        make_creds_from_account(phldef_conduit.ALICE),
        make_creds_from_account(phldef_conduit.BOB))
    fixture.setup_arcyds(arcyd_user, arcyd_email, arcyd_cert, phab_uri)

    yield fixture.arcyds[0]

    fixture.close()


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_exercise_daemon(self):
        with setup_arcyd() as arcyd:
            # [ A] daemon is not started by default
            self.assertFalse(arcyd._has_started_daemon)
            with arcyd.daemon_context():
                # [ A] daemon is started within daemon_context
                self.assertTrue(arcyd._has_started_daemon)
            # [ A] daemon is stopped outside daemon_context
            self.assertFalse(arcyd._has_started_daemon)

    def test_B_exercise_overrun_secs(self):
        with setup_arcyd() as arcyd:
            # [ B] overrun secs are not set by default
            self.assertFalse(arcyd._has_set_overrun_secs)
            arcyd.set_overrun_secs(5)
            # [ B] overrun secs are set by set_overrun_secs
            self.assertTrue(arcyd._has_set_overrun_secs)
            config = phlsys_fs.read_text_file(os.path.join(
                arcyd._root_dir, 'configfile')).split()
            overrun_config_index = config.index('--overrun-secs') + 1
            # [ B] set_overrun_secs writes correct value to config
            self.assertEqual(5, int(config[overrun_config_index]))

    def test_C_exercise_wait_cycles(self):
        with setup_arcyd() as arcyd:
            # [ C] count_cycles is disabled by default
            self.assertFalse(arcyd._has_enabled_count_cycles)
            arcyd.enable_count_cycles_script()
            # [ C] count_cycles is enabled by enable_count_cycles_script
            self.assertTrue(arcyd._has_enabled_count_cycles)
            phlsys_fs.write_text_file(os.path.join(
                arcyd._root_dir, 'cycle_counter'), '2')
            with phlsys_fs.chdir_context(arcyd._root_dir):
                os.system("./count_cycles.sh")
            # [ C] correct number of cycles counted - 3 (2 + 1)
            self.assertEqual(3, arcyd.count_cycles())

    def test_D_exercise_read_log(self):
        with setup_arcyd() as arcyd:
            debug_log_path = '{}/var/log/debug'.format(arcyd._root_dir)
            phlsys_fs.write_text_file(debug_log_path, 'debug log entry')
            info_log_path = '{}/var/log/info'.format(arcyd._root_dir)
            phlsys_fs.write_text_file(info_log_path, 'info log entry')
            info_log = arcyd.info_log()
            debug_log = arcyd.debug_log()
            # [ D] info_log returns correct info log
            self.assertIn('info log entry', info_log)
            # [ D] debug_log returns correct debug log
            self.assertIn('debug log entry', debug_log)

# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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
