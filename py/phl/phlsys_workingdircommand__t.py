"""Test suite for phlsys_workingdircommand."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] command is executed correctly
# [ A] working directory is restored after command execution
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_command_with_working_directory
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import stat
import tempfile
import unittest

import phlsys_fs
import phlsys_workingdircommand


_PYCAT_COMMAND = """
#! /bin/sh
echo "Hello $1!"
""" .lstrip()


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_command_with_working_directory(self):
        working_dir = tempfile.mkdtemp()
        with phlsys_fs.chtmpdir_context():
            tmp_dir = os.getcwd()
            pycat_script_path = os.path.join(tmp_dir, 'pycat.sh')
            phlsys_fs.write_text_file(pycat_script_path, _PYCAT_COMMAND)
            mode = os.stat(pycat_script_path).st_mode
            os.chmod(pycat_script_path, mode | stat.S_IEXEC)

            self.assertEqual(os.getcwd(), tmp_dir)
            command = phlsys_workingdircommand.CommandWithWorkingDirectory(
                pycat_script_path, working_dir)
            result = command('Alice')
            # [ A] command is executed correctly
            self.assertEqual('Hello Alice!\n', result)
            # [ A] working directory is restored after command execution
            self.assertEqual(os.getcwd(), tmp_dir)


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
