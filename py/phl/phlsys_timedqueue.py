"""Priority queue for objects with associated delays.

Usage example:
    >>> tq = TimedQueue(); tq.push('a', datetime.timedelta()); tq.pop_expired()
    ['a']
"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_timedqueue
#
# Public Classes:
#   TimedQueue
#    .push
#    .pop_expired
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import datetime
import heapq


class TimedQueue(object):

    def __init__(self):
        self._items = []
        self._counter = 0

    def push(self, item, delay):
        # here we use counter as a second item in the tuple to compare to make
        # sure that heappush() never tries to compare two items, also to be
        # sure that things come out in the same order they are pushed
        heap_item = (datetime.datetime.now() + delay, self._counter, item)
        self._counter += 1

        heapq.heappush(self._items, heap_item)

    def pop_expired(self):
        expired = []
        if self._items:
            now = datetime.datetime.now()
            while self._items and self._items[0][0] <= now:
                expired.append(heapq.heappop(self._items)[2])
        return expired


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
