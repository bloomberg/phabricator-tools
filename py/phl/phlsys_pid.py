"""Work with process ids easily."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_pid
#
# Public Functions:
#   get
#   is_running
#   request_terminate
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import errno
import os
import signal


def get():
    """Return the integer pid of the current process.

    :returns: int

    """
    return os.getpid()


def is_running(pid):
    """Return True if 'pid' is a running process."""

    # XXX: make sure we're UNIX not Windows

    if pid <= 0:
        # this is not a valid pid
        return False

    try:
        os.kill(pid, 0)  # signal 0 doesn't kill, it just checks
    except OSError as err:
        if err.errno == errno.ESRCH:
            # The pid or process group does not exist.  Note that an  existing
            # process  might  be  a  zombie, a process which already committed
            # termination, but has not yet been wait(2)ed for.
            return False
        elif err.errno == errno.EPERM:
            # The  process  does not have permission to send the signal to any
            # of the target processes.
            return True
        else:
            raise

    return True


def request_terminate(pid):
    """Signal the specified 'pid' to terminate.

    The process may ignore this signal.

    :pid: integer pid, as returned by get()

    """
    os.kill(pid, signal.SIGTERM)


#------------------------------------------------------------------------------
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
#------------------------------- END-OF-FILE ----------------------------------
