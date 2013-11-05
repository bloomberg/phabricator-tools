"""Conveniently retry exception-prone operations."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_tryloop
#
# Public Functions:
#   make_delay_secs_repeats
#   make_default_short_retry
#   make_default_endless_retry
#   try_loop_delay
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import datetime
import itertools
import time


def make_delay_secs_repeats(seconds, repeats):
    """Return a list of delays of the specified 'seconds', 'repeats' long.

    The output suitable for use with 'try_loop_delay'.

    Usage example:
        >>> make_delay_secs_repeats(10, 2)
        [datetime.timedelta(0, 10), datetime.timedelta(0, 10)]

    :seconds: the number of seconds to wait for
    :repeats: how many times to wait
    :returns: a list of datetime.timedelta

    """
    return [datetime.timedelta(seconds=seconds)] * repeats


def make_default_short_retry():
    """Return a list of delays suitable as a 'default' retry.

    The output suitable for use with 'try_loop_delay'.

    :returns: a list of datetime.timedelta

    """
    return make_delay_secs_repeats(seconds=3, repeats=3)


def make_default_endless_retry():
    """Return an endless iterable of delays suitable as a 'default' retry.

    The output suitable for use with 'try_loop_delay'.

    This is the sort of thing you might want to use if you are willing to retry
    something forever.

    The delays used gradually increase so that whichever system is being tried
    is not overly stressed.

    :returns: an endless iterable of datetime.timedelta

    """
    delays = []

    delays += [datetime.timedelta(seconds=1)] * 5
    delays += [datetime.timedelta(seconds=10)] * 5
    delays += [datetime.timedelta(minutes=1)] * 5

    forever = itertools.repeat(datetime.timedelta(minutes=10))
    delays = itertools.chain(delays, forever)

    return delays


def try_loop_delay(
        toTry, delays, exceptionToIgnore=Exception, onException=None):
    """Return the value returned by the supplied 'toTry' operation.

    If 'toTry()' raises an 'exceptionToIgnore' then do 'onException(e, delay)'
    if 'onException' is supplied, where 'e' is the exception object and
    'delay' is the next delay.  Note that 'delay' will be None on the last try.

    The function will continue looping until it runs out of delays or 'toTry()'
    stops raising 'exceptionToIgnore'.

    :toTry: a function which takes no parameters
    :delays: an iterable of datetime.timedelta
    :exceptionToIgnore: class of exception to ignore, defaults to 'Exception'
    :onException: function taking (exception, delay)
    :returns: return value from toTry()

    """
    # TODO: None may arise by mistake in 'delays', use a unique object as
    #       sentinel
    for delay in itertools.chain(delays, [None]):
        try:
            return toTry()
        except exceptionToIgnore as e:
            if onException is not None:
                onException(e, delay)
            if delay is None:
                raise e
        time.sleep(delay.total_seconds())


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
