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

from __future__ import absolute_import

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
