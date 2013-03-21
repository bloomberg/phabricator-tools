#!/usr/bin/env python
import unittest
import subprocess

import utils
from phlsys_subprocess import (run,
                               runCommands,
                               RunResult)


class PhlsysSubprocessTests(unittest.TestCase):
    def test_run_valid_simple_cmd(self):
        "Valid simple cmd - run returns equal RunResult instance"
        args = ("echo", "hello stdout")
        result = run(*args)
        expect = RunResult(stdout=args[1] + "\n", stderr='')
        self.assertEqual(result, expect)

    def test_run_list(self):
        "Passing valid list on stdin sorted in reverse order"
        args = ("sort", "-r")
        kwargs = {"stdin": "1\n2\n3"}
        result = run(*args, **kwargs)
        expect = RunResult(stdout=kwargs['stdin'][::-1] + "\n", stderr='')
        self.assertEqual(result, expect)

    def test_invalid_cmd(self):
        "Passing invalid command - catch OSError"
        with utils.nostd() as stderr:
            self.assertRaises(OSError, run, "invalidcmd")
            self.assertTrue("OSError" in stderr.out)

    def test_invalid_kwargs(self):
        "Passing unexpected kwargs - catch assertion error"
        self.assertRaises(
            AssertionError,
            run, workingDir='foo', stdin='bar', unexpected='foo')

    def test_invalid_return_code(self):
        "Passing command returns non zero exit status"
        with utils.nostd() as stderr:
            cmd = "time"
            self.assertRaises(subprocess.CalledProcessError, run, cmd)
            self.assertTrue(cmd in stderr.out)

    def test_run_commands(self):
        "Run simple cmds - returns None"
        self.assertEqual(None, runCommands("echo hello stdout"))

    def test_run_multi_commands(self):
        "Run multiple cmds - returns None"
        self.assertEqual(None, runCommands(
            "echo hello stdout", "echo goodbye stdout"))

    def test_assertion_raised(self):
        "Assertion raised on bad character input"
        for bad in ("'", '"', '`'):
            self.assertRaises(
                AssertionError,
                runCommands, "echo {0}hello stdout{0}".format(bad))

    def test_invalid_return_code_run_commands(self):
        "Passing incorrect commands returns non zero exit status"
        with utils.nostd() as stderr:
            cmd = "time"
            self.assertRaises(subprocess.CalledProcessError, runCommands, cmd)
            self.assertTrue(cmd in stderr.out)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(PhlsysSubprocessTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
