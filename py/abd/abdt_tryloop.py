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
