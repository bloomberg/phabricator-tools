"""Conveniently schedule unreliable tasks, retry them after a delay."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_scheduleunreliables
#
# Public Classes:
#   DelayedRetryNotifyOperation
#    .do
#    .getDelay
#
# Public Functions:
#   process_loop_forever
#   process_once
#   make_timed_queue
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlsys_timedqueue


def process_loop_forever(operations):
    # use a copy of the original, as we may modify it
    # we need to do set operations so 'set' is most appropriate
    operations = set(operations)

    paused_operations = phlsys_timedqueue.TimedQueue()

    while True:
        _process_operations(operations, paused_operations)


def process_once(operations):
    """Return the set of still active operations after processing each once.

    :operations: an iterable of objects that support 'do' and 'getDelay'
    :returns: a set of the still active operations after processing each once.

    """
    # use a copy of the original, as we may modify it
    # we need to do set operations so 'set' is most appropriate
    operations = set(operations)

    paused_operations = phlsys_timedqueue.TimedQueue()

    _process_operations(operations, paused_operations)

    return operations


def make_timed_queue():
    return phlsys_timedqueue.TimedQueue()


def _process_operations(operations, paused_operations):
    assert isinstance(operations, set)
    operations |= set(paused_operations.pop_expired())

    new_bad_operations = set()
    for op in operations:
        if not op.do():
            new_bad_operations.add(op)

    if new_bad_operations:
        operations -= new_bad_operations
        for op in new_bad_operations:
            delay = op.getDelay()
            if delay is not None:
                paused_operations.push(op, delay)


class DelayedRetryNotifyOperation(object):
    # TODO: support iterables generally

    def __init__(self, operation, delays, on_exception=None):
        self._op = operation
        self._delays = list(delays)  # we want our own copy since we'll modify
        self._on_exception = on_exception

    def do(self):
        next_delay = None if not self._delays else self._delays[0]
        is_ok = False
        try:
            self._op()
            is_ok = True
        except Exception:
            if self._on_exception:
                self._on_exception(next_delay)
            else:
                raise
        return is_ok

    def getDelay(self):
        delay = None
        if self._delays:
            delay = self._delays.pop(0)
        return delay


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
