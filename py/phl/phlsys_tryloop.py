"""Conveniently retry exception-prone operations."""

import itertools
import time


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
