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
from __future__ import division
from __future__ import print_function

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


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
