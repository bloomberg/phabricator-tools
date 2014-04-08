"""Daemonize the current process."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_daemonize
#
# Public Functions:
#   do
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import os
import sys


def do(stdin_path=None, stdout_path=None, stderr_path=None):
    """Attach this process to a new session, detach stdio.

    This is useful for 'backgrounding' a process in such a way that if the
    originating terminal exits, this process will continue running.

    It also detaches the process from the original stdin, stdout, stderr
    so that this process can continue to function after the originating
    terminal ceases to be.

    Note that it's a good idea to also phlsys_signal.set_exit_on_sigterm()
    so that this process can exit gracefully if killed.

    :stdin_path: path to read from as stdin
    :stdout_path: path to write as stdout
    :stderr_path: path to write as stderr
    :returns: None

    """
    if os.fork():
        # there are now two copies of our original process, quit the original
        os._exit(0)

    # attach the process to a whole new session, so we'll not receive SIGHUP if
    # the original terminal exits etc.
    os.setsid()

    # fork again and exit the original, which would have been the session
    # leader.  this appears to be necessary to prevent our daemon from
    # attaching to a controlling terminal, which can only happen to a session
    # leader.
    #
    if os.fork():
        # there are now two copies of our new process, quit the first one
        os._exit(0)

    # detach from existing standard IO
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()

    # attach to the specified new standard io, or just devnull if nothing was
    # specified. this is important, if it wasn't done then any call to print()
    # after the original terminal exits would fail and potentially exit the
    # daemon.
    #
    # use line buffering on the output files so it's possible to monitor them,
    # otherwise the contents will only be available if / when this process
    # exits gracefully.
    #
    line_buffered = 1
    sys.stdin = open(
        stdin_path if stdin_path is not None else os.devnull, 'r')
    sys.stdout = open(
        stdout_path if stdout_path is not None else os.devnull,
        'w',
        line_buffered)
    sys.stderr = open(
        stderr_path if stderr_path is not None else os.devnull,
        'w',
        line_buffered)


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
# ------------------------------ END-OF-FILE ----------------------------------
