from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import phlsys_fs
import phlsys_subprocess


class PhlsysSubprocessTests(unittest.TestCase):

    def test_run_valid_simple_cmd(self):
        "Valid simple cmd - run returns equal RunResult instance"
        args = ("echo", "hello stdout")
        result = phlsys_subprocess.run(*args)
        expect = phlsys_subprocess.RunResult(stdout=args[1] + "\n", stderr='')
        self.assertEqual(result, expect)

    def test_run_list(self):
        """Passing valid list on stdin sorted in reverse order."""
        args = ("sort", "-r")
        kwargs = {"stdin": "1\n2\n3"}
        result = phlsys_subprocess.run(*args, **kwargs)
        expect = phlsys_subprocess.RunResult(
            stdout=kwargs['stdin'][::-1] + "\n", stderr='')
        self.assertEqual(result, expect)

    def test_invalid_cmd(self):
        "Passing invalid command - catch OSError"
        with phlsys_fs.nostd() as stderr:
            self.assertRaises(OSError, phlsys_subprocess.run, "invalidcmd")
            self.assertTrue("OSError" in stderr.out)

    def test_invalid_kwargs(self):
        "Passing unexpected kwargs - catch assertion error"
        self.assertRaises(
            AssertionError,
            phlsys_subprocess.run,
            workingDir='foo',
            stdin='bar',
            unexpected='foo')

    def test_invalid_return_code(self):
        """Passing command returns non zero exit status."""
        cmd = "time"
        self.assertRaises(
            phlsys_subprocess.CalledProcessError,
            phlsys_subprocess.run,
            cmd)

    def test_run_commands(self):
        "Run simple cmds - returns None"
        self.assertEqual(
            None, phlsys_subprocess.run_commands("echo hello stdout"))

    def test_run_multi_commands(self):
        "Run multiple cmds - returns None"
        self.assertEqual(None, phlsys_subprocess.run_commands(
            "echo hello stdout", "echo goodbye stdout"))

    def test_assertion_raised(self):
        """Assertion raised on bad character input."""
        for bad in ("'", '"', '`'):
            self.assertRaises(
                AssertionError,
                phlsys_subprocess.run_commands,
                "echo {0}hello stdout{0}".format(bad))

    def test_invalid_return_code_run_commands(self):
        """Passing incorrect commands returns non zero exit status."""
        cmd = "time"
        self.assertRaises(
            phlsys_subprocess.CalledProcessError,
            phlsys_subprocess.run_commands,
            cmd)
        # self.assertTrue(cmd in stderr.out)


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
