"""Helpers for process signals."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_signal
#
# Public Classes:
#   SignalFlags
#
# Public Functions:
#   no_exit_context
#   set_exit_on_sigterm
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
import signal
import sys


class SignalFlags(object):

    def __init__(self):
        self.got_sigterm = False
        self.delay_sigterm_exit_level = 0


_SIGNAL_FLAGS = SignalFlags()


@contextlib.contextmanager
def no_exit_context():
    _SIGNAL_FLAGS.delay_sigterm_exit_level += 1
    try:
        yield
    except:
        level = _SIGNAL_FLAGS.delay_sigterm_exit_level
        if level == 1 and _SIGNAL_FLAGS.got_sigterm:
            # Replace the current exception, as we must now exit and the other
            # exception might be caught and continued from.
            # Raise 'SystemExit' exception, which will allow us to clean up.
            sys.exit(1)
        else:
            raise
    else:
        level = _SIGNAL_FLAGS.delay_sigterm_exit_level
        if level == 1 and _SIGNAL_FLAGS.got_sigterm:
            # raises 'SystemExit' exception, which will allow us to clean up
            sys.exit(1)
    finally:
        _SIGNAL_FLAGS.delay_sigterm_exit_level -= 1


def set_exit_on_sigterm():

    def HandleSigterm(unused1, unused2):
        _SIGNAL_FLAGS.got_sigterm = True
        if not _SIGNAL_FLAGS.delay_sigterm_exit_level:
            # raises 'SystemExit' exception, which will allow us to clean up
            sys.exit(1)

    signal.signal(signal.SIGTERM, HandleSigterm)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2016 Bloomberg Finance L.P.
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
