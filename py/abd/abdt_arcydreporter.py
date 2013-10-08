"""Report the state of arcyd as it updates repositories."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_arcydreporter
#
# Public Classes:
#   Timer
#    .start
#    .stop
#    .duration
#   ArcydReporter
#    .start_sleep
#    .update_sleep
#    .on_tryloop_exception
#    .log_system_error
#    .log_system_exception
#    .finish_sleep
#    .start_cache_refresh
#    .finish_cache_refresh
#    .start_repo
#    .tag_timer_context
#    .tag_timer_decorate_object_methods
#    .tag_timer_decorate_object_methods_individually
#    .fail_repo
#    .finish_repo
#    .close
#
# Public Functions:
#   timer_context
#
# Public Assignments:
#   ARCYD_STATUS
#   ARCYD_STATUS_DESCRIPTION
#   ARCYD_CURRENT_REPO
#   ARCYD_REPOS
#   ARCYD_STATISTICS
#   ARCYD_LOG_SYSTEM_ERROR
#   ARCYD_LIST_ATTRIB
#   ARCYD_STATUS_STARTING
#   ARCYD_STATUS_UPDATING
#   ARCYD_STATUS_SLEEPING
#   ARCYD_STATUS_REFRESHING_CACHE
#   ARCYD_STATUS_STOPPED
#   ARCYD_STATUS_IDLE
#   ARCYD_STATUS_TRYLOOP_EXCEPTION
#   ARCYD_LIST_STATUS
#   REPO_ATTRIB_NAME
#   REPO_ATTRIB_HUMAN_NAME
#   REPO_ATTRIB_STATUS
#   REPO_LIST_ATTRIB
#   REPO_STATUS_UPDATING
#   REPO_STATUS_FAILED
#   REPO_STATUS_OK
#   REPO_STATUSES
#   ARCYD_STAT_CURRENT_CYCLE_TIME
#   ARCYD_STAT_LAST_CYCLE_TIME
#   ARCYD_STAT_TAG_TIMES
#   ARCYD_LIST_STATISTICS
#   ARCYD_LOGITEM_DATETIME
#   ARCYD_LOGITEM_IDENTIFIER
#   ARCYD_LOGITEM_DETAIL
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections
import contextlib
import datetime
import functools
import inspect
import traceback
import types


ARCYD_STATUS = 'status'
ARCYD_STATUS_DESCRIPTION = 'status-description'
ARCYD_CURRENT_REPO = 'current-repo'
ARCYD_REPOS = 'repos'
ARCYD_STATISTICS = 'statistics'
ARCYD_LOG_SYSTEM_ERROR = 'log-system-error'
# ARCYD_LOG_USER_ERROR = 'log-user-error'
# ARCYD_LOG_USER_ACTION = 'log-user-action'

ARCYD_LIST_ATTRIB = [
    ARCYD_CURRENT_REPO,
    ARCYD_STATUS,
    ARCYD_STATUS_DESCRIPTION,
    ARCYD_REPOS,
    ARCYD_STATISTICS,
    ARCYD_LOG_SYSTEM_ERROR,
]

ARCYD_STATUS_STARTING = 'starting'
ARCYD_STATUS_UPDATING = 'updating'
ARCYD_STATUS_SLEEPING = 'sleeping'
ARCYD_STATUS_REFRESHING_CACHE = 'refreshing-cache'
ARCYD_STATUS_STOPPED = 'stopped'
ARCYD_STATUS_IDLE = 'idle'
ARCYD_STATUS_TRYLOOP_EXCEPTION = 'tryloop-exception'

ARCYD_LIST_STATUS = [
    ARCYD_STATUS_UPDATING,
    ARCYD_STATUS_SLEEPING,
    ARCYD_STATUS_REFRESHING_CACHE,
    ARCYD_STATUS_STARTING,
    ARCYD_STATUS_STOPPED,
    ARCYD_STATUS_IDLE,
    ARCYD_STATUS_TRYLOOP_EXCEPTION,
]

REPO_ATTRIB_NAME = 'name'
REPO_ATTRIB_HUMAN_NAME = 'human-name'
REPO_ATTRIB_STATUS = 'repo-status'

REPO_LIST_ATTRIB = [
    REPO_ATTRIB_NAME,
    REPO_ATTRIB_HUMAN_NAME,
    REPO_ATTRIB_STATUS,
]

REPO_STATUS_UPDATING = 'updating'
REPO_STATUS_FAILED = 'failed'
REPO_STATUS_OK = 'ok'

REPO_STATUSES = [
    REPO_STATUS_UPDATING,
    REPO_STATUS_FAILED,
    REPO_STATUS_OK,
]

ARCYD_STAT_CURRENT_CYCLE_TIME = 'current-cycle-time'
ARCYD_STAT_LAST_CYCLE_TIME = 'last-cycle-time'
ARCYD_STAT_TAG_TIMES = 'tag-times'

ARCYD_LIST_STATISTICS = [
    ARCYD_STAT_CURRENT_CYCLE_TIME,
    ARCYD_STAT_LAST_CYCLE_TIME,
    ARCYD_STAT_TAG_TIMES,
]

ARCYD_LOGITEM_DATETIME = 'logitem-datetime'
ARCYD_LOGITEM_IDENTIFIER = 'logitem-identifier'
ARCYD_LOGITEM_DETAIL = 'logitem-detail'


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


class _CycleTimer(object):

    def __init__(self):
        self._current_start = None
        self._last_duration = None

    def start_cycle(self):
        self._current_start = datetime.datetime.utcnow()

    def stop_cycle(self):
        self._last_duration = self.current_duration()
        self._current_start = None

    def current_duration(self):
        if self._current_start is None:
            return None
        duration = datetime.datetime.utcnow() - self._current_start
        return duration.total_seconds()

    @property
    def last_duration(self):
        return self._last_duration


class ArcydReporter(object):

    def __init__(self, output):
        """Initialise a new reporter to report to the specified outputs.

        :output: output to write status to

        """
        super(ArcydReporter, self).__init__()
        self._output = output

        assert self._output

        self._repos = {}
        self._repo = None

        self._cycle_timer = _CycleTimer()
        self._tag_times = collections.defaultdict(float)
        self._log_system_error = list()

        self._write_status(ARCYD_STATUS_STARTING)

    def start_sleep(self, duration):
        _ = duration  # NOQA
        self._cycle_timer.stop_cycle()
        self._write_status(ARCYD_STATUS_SLEEPING)

    def update_sleep(self, duration):
        _ = duration  # NOQA
        self._write_status(ARCYD_STATUS_SLEEPING)

    def on_tryloop_exception(self, e, delay):
        tb = traceback.format_exc()
        self._write_status(
            ARCYD_STATUS_TRYLOOP_EXCEPTION,
            "will retry in " + str(delay) + '\n' + str(e) + '\n\n' + tb)

    def _add_log_item(self, log, identifier, detail):
        now = str(datetime.datetime.utcnow())
        d = {
            ARCYD_LOGITEM_DATETIME: now,
            ARCYD_LOGITEM_IDENTIFIER: identifier,
            ARCYD_LOGITEM_DETAIL: detail,
        }
        log.append(d)

    def log_system_error(self, identifier, detail):
        self._add_log_item(self._log_system_error, identifier, detail)

    def log_system_exception(self, identifier, detail, exception):
        message = detail + '\n' + repr(exception)
        self.log_system_error(identifier, message)

    def finish_sleep(self):
        self._write_status(ARCYD_STATUS_IDLE)
        self._cycle_timer.start_cycle()

    def start_cache_refresh(self):
        self._write_status(ARCYD_STATUS_REFRESHING_CACHE)

    def finish_cache_refresh(self):
        self._write_status(ARCYD_STATUS_IDLE)

    def start_repo(self, name, human_name):
        self._repo = {
            REPO_ATTRIB_NAME: name,
            REPO_ATTRIB_HUMAN_NAME: human_name,
            REPO_ATTRIB_STATUS: REPO_STATUS_UPDATING,
        }
        self._write_status(ARCYD_STATUS_UPDATING)

    @contextlib.contextmanager
    def tag_timer_context(self, tag_name):
        with timer_context() as timer:
            yield
        self._tag_times[tag_name] += timer.duration

    def _tag_timer_decorate(self, tag, f):
        @functools.wraps(f)
        def wrapper(other_self, *args, **kwargs):
            with self.tag_timer_context(tag):
                return f(other_self, *args, **kwargs)
        return wrapper

    def tag_timer_decorate_object_methods(self, object_, tag):
        for name, attribute in object_.__class__.__dict__.iteritems():
            if inspect.isfunction(attribute):
                new_method = types.MethodType(
                    self._tag_timer_decorate(tag, attribute), object_)
                object_.__dict__[name] = new_method

    def tag_timer_decorate_object_methods_individually(self, object_, tag):
        for name, attribute in object_.__class__.__dict__.iteritems():
            if inspect.isfunction(attribute):
                description = '.'.join([tag, name])
                new_method = types.MethodType(
                    self._tag_timer_decorate(description, attribute), object_)
                object_.__dict__[name] = new_method

    def fail_repo(self):
        self._repo[REPO_ATTRIB_STATUS] = REPO_STATUS_FAILED
        self._repos[self._repo[REPO_ATTRIB_NAME]] = self._repo
        self._repo = None
        self._write_status(ARCYD_STATUS_UPDATING)

    def finish_repo(self):
        if self._repo is None:
            # if we fail_repo then we'll finish_repo after so allow
            # finishing when there's no current repo
            # (we still want to set the repo to None in fail_repo or we'll
            #  accidentally set it to OK in this function)
            return
        self._repo[REPO_ATTRIB_STATUS] = REPO_STATUS_OK
        self._repos[self._repo[REPO_ATTRIB_NAME]] = self._repo
        self._repo = None
        self._write_status(ARCYD_STATUS_IDLE)

    def _write_status(self, status, description=None):
        timer = self._cycle_timer
        assert status in ARCYD_LIST_STATUS
        statistics = {
            ARCYD_STAT_CURRENT_CYCLE_TIME: timer.current_duration(),
            ARCYD_STAT_LAST_CYCLE_TIME: timer.last_duration,
            ARCYD_STAT_TAG_TIMES: self._tag_times,
        }
        assert set(statistics.keys()) == set(ARCYD_LIST_STATISTICS)
        d = {
            ARCYD_STATUS: status,
            ARCYD_STATUS_DESCRIPTION: description,
            ARCYD_CURRENT_REPO: self._repo,
            ARCYD_REPOS: [self._repos[k] for k in self._repos],
            ARCYD_STATISTICS: statistics,
            ARCYD_LOG_SYSTEM_ERROR: self._log_system_error,
        }
        assert set(d.keys()) == set(ARCYD_LIST_ATTRIB)
        self._output.write(d)

    def close(self):
        self._write_status(ARCYD_STATUS_STOPPED)


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
