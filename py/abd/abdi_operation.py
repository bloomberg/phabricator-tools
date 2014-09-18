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
#   KillFileError
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


class KillFileError(Exception):
    pass


class CheckSpecialFiles(object):

    def __init__(self, kill_file):
        self._kill_file = kill_file

    def do(self):
        if self._kill_file and os.path.isfile(self._kill_file):
            os.remove(self._kill_file)
            raise KillFileError("kill file: " + self._kill_file)
        return True


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
