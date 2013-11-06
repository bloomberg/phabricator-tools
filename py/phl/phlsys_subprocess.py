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
        error_msg = "cmd: {0}\n".format(" ".join(cmd))
        if workingDir:
            error_msg += "workingDir: {0}\n".format(workingDir)
        if stdin:
            error_msg += "stdin: {0}\n".format(stdin)
        error_msg += "out: {0}\nerr: {1}\n".format(out, err)
        sys.stderr.write(error_msg)
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
