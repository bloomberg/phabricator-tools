"""Conveniently retry exception-prone operations."""

import datetime
import itertools
import time


def tryLoopDelay(toTry, startLoop, ifException, ifBaseException, delays):
    _validateDelays(delays)
    for delay in itertools.chain(delays, [None]):
        startLoop()

        try:
            toTry()
            return
        except Exception:
            ifException(delay)
        except BaseException:
            ifBaseException(delay)

        if delay is not None:
            time.sleep(datetime.timedelta(**delay).total_seconds())


def _validateDelays(retry_delays):
    """if there's a problem in the retry delays, it's better to fail early."""
    for retry_delay in retry_delays:
        datetime.timedelta(**retry_delay).total_seconds()


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
