"""Arcyd operations that can be scheduled with phlsys_scheduleunreliables."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_operation
#
# Public Classes:
#   Sleep
#    .do
#   RefreshCaches
#    .do
#   ResetFileError
#   CheckSpecialFiles
#    .do
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import os
import time

import abdt_errident
import abdt_tryloop


class Sleep(object):

    def __init__(self, secs, reporter):
        self._secs = secs
        self._reporter = reporter

    def do(self):
        sleep_remaining = self._secs
        self._reporter.start_sleep(sleep_remaining)
        while sleep_remaining > 0:
            self._reporter.update_sleep(sleep_remaining)
            time.sleep(1)
            sleep_remaining -= 1
        self._reporter.finish_sleep()
        return True


class RefreshCaches(object):

    def __init__(self, conduits, url_watcher, reporter):
        super(RefreshCaches, self).__init__()
        self._conduits = conduits
        self._url_watcher = url_watcher
        self._reporter = reporter

    def do(self):
        self._reporter.start_cache_refresh()

        with self._reporter.tag_timer_context('refresh conduit cache'):
            for key in self._conduits:
                conduit = self._conduits[key]
                abdt_tryloop.critical_tryloop(
                    conduit.refresh_cache_on_cycle,
                    abdt_errident.CONDUIT_REFRESH,
                    conduit.describe())

        with self._reporter.tag_timer_context('refresh git watcher'):
            abdt_tryloop.critical_tryloop(
                self._url_watcher.refresh, abdt_errident.GIT_SNOOP, '')

        self._reporter.finish_cache_refresh()
        return True


class ResetFileError(Exception):

    def __init__(self, path):
        self.path = path
        super(ResetFileError, self).__init__()


class CheckSpecialFiles(object):

    def __init__(self, kill_file, reset_file, pause_file, on_pause):
        self._kill_file = kill_file
        self._reset_file = reset_file
        self._pause_file = pause_file
        self._on_pause = on_pause

    def do(self):
        if self._kill_file and os.path.isfile(self._kill_file):
            os.remove(self._kill_file)
            raise Exception("kill file: " + self._kill_file)
        if self._reset_file and os.path.isfile(self._reset_file):
            raise ResetFileError(self._reset_file)
        if self._pause_file and os.path.isfile(self._pause_file):
            if self._on_pause:
                self._on_pause()
            while os.path.isfile(self._pause_file):
                time.sleep(1)
        return True


#------------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
