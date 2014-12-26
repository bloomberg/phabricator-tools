"""Retry operations that may intermittently fail, log each failure."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_tryloop
#
# Public Functions:
#   tryloop
#   critical_tryloop
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import phlsys_tryloop

import abdt_logging


def tryloop(f, identifier, detail):
    """Return the result of the supplied operation 'f', retry on exception.

    Will retry operation 'f' after a short delay if it raises, gives up after
    a few attempts.

    :f: a callable that can be invoked like so 'f()'
    :identifier: a short string identifier for the calling line of code
    :detail: a string of the variables associated with the call, e.g. repo name
    :returns: the return value of operation 'f', if successful

    """
    def on_tryloop_exception(e, delay):
        abdt_logging.on_retry_exception(identifier, detail, e, delay)

    delays = phlsys_tryloop.make_default_short_retry()

    return phlsys_tryloop.try_loop_delay(
        f, delays, onException=on_tryloop_exception)


def critical_tryloop(f, identifier, detail):
    """Return the result of the supplied operation 'f', retry on exception.

    Will retry operation 'f' indefinitely until it does not raise, the delays
    used gradually increase so that whichever system is being tried is not
    overly stressed.

    :f: a callable that can be invoked like so 'f()'
    :identifier: a short string identifier for the calling line of code
    :detail: a string of the variables associated with the call, e.g. repo name
    :returns: the return value of operation 'f', if successful

    """
    def on_tryloop_exception(e, delay):
        abdt_logging.on_retry_exception(identifier, detail, e, delay)

    delays = phlsys_tryloop.make_default_endless_retry()

    return phlsys_tryloop.try_loop_delay(
        f, delays, onException=on_tryloop_exception)


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
