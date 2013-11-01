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
