"""Determine the wall clock duration of events."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_timer
#
# Public Classes:
#   Timer
#    .start
#    .stop
#    .restart
#    .duration
#
# Public Functions:
#   print_duration_context
#   timer_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import datetime


@contextlib.contextmanager
def print_duration_context(name):
    with timer_context() as t:
        yield
        print "{} took {} secs".format(name, t.duration)


@contextlib.contextmanager
def timer_context():
    timer = Timer()
    timer.start()
    try:
        yield timer
    finally:
        timer.stop()


class Timer(object):

    def __init__(self):
        self._start = None
        self._stop = None
        self._duration = None

    def start(self):
        self._start = datetime.datetime.utcnow()
        self._stop = None
        self._duration = None

    def stop(self):
        assert self._start is not None
        self._stop = datetime.datetime.utcnow()

    def restart(self):
        """Start the timer, return the previous duration.

        If there is no previous duration then return 0.0.

        Usage example:
            >>> timer = Timer()
            >>> timer.restart() >= 0.0
            True
            >>> timer.restart() >= 0.0
            True

        :returns: a floating point number of seconds

        """
        duration = 0.0
        if self._start is not None:
            duration = self.duration

        self.start()
        return duration

    @property
    def duration(self):
        if self._duration is None:
            assert self._start is not None
            if self._stop is None:
                duration = datetime.datetime.utcnow() - self._start
                duration = duration.total_seconds()
                return duration
            self._duration = self._stop - self._start
            self._duration = self._duration.total_seconds()
        return self._duration


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
