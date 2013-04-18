#!/usr/bin/env python
# encoding: utf-8

"""Interact with other programs using command-line semantics."""

import collections
import doctest
import subprocess
import sys

RunResult = collections.namedtuple(
    'phlsys_subprocess__RunResult',
    ['stdout', 'stderr'])


#def run(*args, workingDir=None): <-- supported in Python 3, use kwargs for now
def run(*args, **kwargs):
    """Execute the command described by args, return a 'RunResult'.

    This is a convenience function which wraps the functionality of
    subprocess.Popen() in a manner more compatible for our uses here.

    Raise a 'subprocess.CalledProcessError' if the return code is not equal to
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
    if (p.returncode != 0):
        error_msg = "cmd: {0}\n".format(" ".join(cmd))
        if workingDir:
            error_msg += "workingDir: {0}\n".format(workingDir)
        if stdin:
            error_msg += "stdin: {0}\n".format(stdin)
        error_msg += "out: {0}\nerr: {1}\n".format(out, err)
        sys.stderr.write(error_msg)
        raise subprocess.CalledProcessError(p.returncode, cmd, out)
    return RunResult(stdout=out, stderr=err)


# XXX: doesn't handle quotes or backticks
def runCommands(*commands):
    """Execute the command-line strings descripted by '*commands'.

    This is a convenience function which wraps the functionality of
    run() in a manner more compatible for test cases.

    Raise a 'subprocess.CalledProcessError' if the return code is not equal to
    zero; also echo extra information to stderr.

    Note that behaviour is undefined in the presense of quotes and backticks.

    Usage examples:
        Echoing 'hello stdout' to stdout:
        >>> runCommands('echo hello stdout')

        Echoing 'hello stdout' 'goodbye stdout' to stdout:
        >>> runCommands('echo hello stdout', 'echo goodbye stdout')

    :*commands: a list of strings corresponding to command-lines
    :returns: None

    """
    assert not any(bad in c for c in commands for bad in ("'", '"', '`'))

    for c in commands:
        run(*c.split())


if __name__ == "__main__":
    doctest.testmod()

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
