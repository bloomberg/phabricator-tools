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
        "Passing valid list on stdin sorted in reverse order"
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
        "Passing command returns non zero exit status"
        with phlsys_fs.nostd() as stderr:
            cmd = "time"
            self.assertRaises(
                phlsys_subprocess.CalledProcessError,
                phlsys_subprocess.run,
                cmd)
            self.assertTrue(cmd in stderr.out)

    def test_run_commands(self):
        "Run simple cmds - returns None"
        self.assertEqual(
            None, phlsys_subprocess.run_commands("echo hello stdout"))

    def test_run_multi_commands(self):
        "Run multiple cmds - returns None"
        self.assertEqual(None, phlsys_subprocess.run_commands(
            "echo hello stdout", "echo goodbye stdout"))

    def test_assertion_raised(self):
        "Assertion raised on bad character input"
        for bad in ("'", '"', '`'):
            self.assertRaises(
                AssertionError,
                phlsys_subprocess.run_commands,
                "echo {0}hello stdout{0}".format(bad))

    def test_invalid_return_code_run_commands(self):
        "Passing incorrect commands returns non zero exit status"
        with phlsys_fs.nostd() as stderr:
            cmd = "time"
            self.assertRaises(
                phlsys_subprocess.CalledProcessError,
                phlsys_subprocess.run_commands,
                cmd)
            self.assertTrue(cmd in stderr.out)


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
