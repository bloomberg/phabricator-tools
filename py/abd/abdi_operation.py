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
#   CycleReportJson
#    .do
#    .getDelay
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import json
import logging
import os
import time

import phlsys_strtotime
import phlsys_subprocess
import phlsys_timer

import abdt_errident
import abdt_tryloop

_LOGGER = logging.getLogger(__name__)


class Sleep(object):

    def __init__(self, secs):
        self._secs = secs

    def do(self):
        sleep_remaining = self._secs
        while sleep_remaining > 0:
            time.sleep(1)
            sleep_remaining -= 1
        return True


class RefreshCaches(object):

    def __init__(self, conduits, url_watcher):
        super(RefreshCaches, self).__init__()
        self._conduits = conduits
        self._url_watcher = url_watcher

    def do(self):
        for key in self._conduits:
            conduit = self._conduits[key]
            abdt_tryloop.critical_tryloop(
                conduit.refresh_cache_on_cycle,
                abdt_errident.CONDUIT_REFRESH,
                conduit.describe())

        abdt_tryloop.critical_tryloop(
            self._url_watcher.refresh, abdt_errident.GIT_SNOOP, '')

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


class CycleReportJson(object):

    "Pipes a json report object to stdin of 'report_command' every cycle."

    def __init__(self, report_command):
        self._report_command = report_command
        self._timer = phlsys_timer.Timer()
        self._timer.start()
        self._is_first_cycle = True

        strToTime = phlsys_strtotime.duration_string_to_time_delta
        self._delays = [strToTime(d) for d in ["10 minutes", "1 hours"]]

    def do(self):

        report = {
            "cycle_time_secs": self._timer.restart(),
        }

        report_json = json.dumps(report)

        # skip actually reporting the first cycle so that we don't get
        # incomplete results - we may not be the last operation to be processed
        #
        if self._is_first_cycle:
            self._is_first_cycle = False
        else:
            try:
                phlsys_subprocess.run(self._report_command, stdin=report_json)
            except phlsys_subprocess.CalledProcessError as e:
                _LOGGER.error("CycleReportJson: {}".format(e))
                return False

        return True

    def getDelay(self):
        delay = None
        if self._delays:
            delay = self._delays.pop(0)
        return delay


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
