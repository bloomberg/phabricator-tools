"""Interact with other programs using command-line semantics."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_subprocess
#
# Public Classes:
#   Error
#   CalledProcessError
#
# Public Functions:
#   run
#   run_commands
#
# Public Assignments:
#   RunResult
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import subprocess
import sys

RunResult = collections.namedtuple(
    'phlsys_subprocess__RunResult',
    ['stdout', 'stderr'])


class Error(Exception):

    """Base class for exceptions in this module."""
    pass


class CalledProcessError(Error):

    """Exception for passing errors from called processes.

    Attributes:
        cmd      -- array, the command used to launch the subprocess
        stdin    -- string, the input supplied to the command
        stdout   -- string, the stdout output from the command
        stderr   -- string, the stderr output from the command
        exitcode -- int, the exitcode from the command

    """

    def __init__(self, cmd, stdin, stdout, stderr, exitcode, workingdir):
        self.cmd = cmd
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.exitcode = exitcode
        self.workingdir = workingdir
        self.msg = "cmd: {0}\n".format(" ".join(cmd))
        if workingdir:
            self.msg += "workingdir: {0}\n".format(workingdir)
        if stdin:
            self.msg += "stdin: {0}\n".format(stdin)
        self.msg += "stdout: {0}\nstderr: {1}\n".format(stdout, stderr)
        super(CalledProcessError, self).__init__(self.msg)


# def run(*args, workingDir=None): <-- supported in Python 3, use kwargs
# for now
def run(*args, **kwargs):
    """Execute the command described by args, return a 'RunResult'.

    This is a convenience function which wraps the functionality of
    subprocess.Popen() in a manner more compatible for our uses here.

    Raise a 'CalledProcessError' if the return code is not equal to
    zero; also echo extra information to stderr.

    Usage examples:
        Echoing 'hello stdout' to stdout:
        >>> run('echo', 'hello stdout')
        phlsys_subprocess__RunResult(stdout='hello stdout\\n', stderr='')

        Passing a list on stdin and sorting in reverse order:
        >>> run('sort', '-r', stdin='1\\n2\\n3')
        phlsys_subprocess__RunResult(stdout='3\\n2\\n1\\n', stderr='')

    :*args: a tuple of strings corresponding to command-line arguments
    :**kwargs: keyword arguments corresponding to the special
    :returns: a RunResult corresponding to the output of the command

    """
    # TODO: allow customization of non-zero return value behaviour,
    #       maybe not all clients will want to raise an exception in this case.
    #       if we do allow this customization then we'll also want to
    #       return the return value via the RunResult
    workingDir = kwargs.pop("workingDir", None)
    stdin = kwargs.pop("stdin", None)
    assert not kwargs
    cmd = args
    try:
        p = subprocess.Popen(
            cmd,
            cwd=workingDir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        out, err = p.communicate(input=stdin)
    except OSError:
        sys.stderr.write(
            "OSError: unable to locate command: {0}\n".format(" ".join(cmd)))
        raise

    # pylint has faulty detection of POpen members:
    # http://www.logilab.org/ticket/46273
    # pylint: disable=E1101
    returncode = p.returncode  # pylint: disable=E1101
    # pylint: enable=E1101

    if (returncode != 0):
        raise CalledProcessError(
            cmd=cmd,
            stdin=stdin,
            stdout=out,
            stderr=err,
            exitcode=returncode,
            workingdir=workingDir)
    return RunResult(stdout=out, stderr=err)


# XXX: doesn't handle quotes or backticks
def run_commands(*commands):
    """Execute the command-line strings descripted by '*commands'.

    This is a convenience function which wraps the functionality of
    run() in a manner more compatible for test cases.

    Raise a 'CalledProcessError' if the return code is not equal to zero

    Note that behaviour is undefined in the presense of quotes and backticks.

    Usage examples:
        Echoing 'hello stdout' to stdout:
        >>> run_commands('echo hello stdout')

        Echoing 'hello stdout' 'goodbye stdout' to stdout:
        >>> run_commands('echo hello stdout', 'echo goodbye stdout')

    :*commands: a list of strings corresponding to command-lines
    :returns: None

    """
    assert not any(bad in c for c in commands for bad in ("'", '"', '`'))

    for c in commands:
        run(*c.split())


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
