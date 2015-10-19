"""Tools to start and manage an Arcyd instance."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# atet_arcyd_instance
#
# Public Classes:
#   ArcydInstance
#    .set_overrun_secs
#    .enable_count_cycles_script
#    .count_cycles
#    .wait_one_or_more_cycles
#    .run_once
#    .start_daemon
#    .stop_daemon
#    .daemon_context
#    .info_log
#    .debug_log
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
import os
import stat
import time

import phlsys_fs
import phlsys_workingdircommand

_EXTERNAL_REPORT_COUNTER = """
#! /bin/sh
if [ ! -f cycle_counter ]; then
    echo 0 > cycle_counter
    fi

COUNT=$(cat cycle_counter)
COUNT=$(expr $COUNT + 1)

echo $COUNT > cycle_counter
""".lstrip()


class ArcydInstance(object):

    def __init__(self, root_dir, arcyd_command):
        self._root_dir = root_dir
        self._command = phlsys_workingdircommand.CommandWithWorkingDirectory(
            arcyd_command, root_dir)

        count_cycles_script_path = os.path.join(
            self._root_dir, 'count_cycles.sh')
        phlsys_fs.write_text_file(
            count_cycles_script_path,
            _EXTERNAL_REPORT_COUNTER)
        mode = os.stat(count_cycles_script_path).st_mode
        os.chmod(count_cycles_script_path, mode | stat.S_IEXEC)

        self._has_enabled_count_cycles = False
        self._has_started_daemon = False
        self._has_set_overrun_secs = False

    def __call__(self, *args, **kwargs):
        return self._command(*args, **kwargs)

    def set_overrun_secs(self, overrun_secs):
        assert not self._has_set_overrun_secs
        config_path = os.path.join(self._root_dir, 'configfile')
        config_text = phlsys_fs.read_text_file(config_path)
        config_text += '\n--overrun-secs\n{}'.format(overrun_secs)
        phlsys_fs.write_text_file(config_path, config_text)
        self._has_set_overrun_secs = True

    def enable_count_cycles_script(self):
        assert not self._has_enabled_count_cycles
        config_path = os.path.join(self._root_dir, 'configfile')
        config_text = phlsys_fs.read_text_file(config_path)
        config_text += '\n--external-report-command\ncount_cycles.sh'
        phlsys_fs.write_text_file(config_path, config_text)
        self._has_enabled_count_cycles = True

    def count_cycles(self):
        assert self._has_enabled_count_cycles
        counter_path = os.path.join(self._root_dir, 'cycle_counter')
        if not os.path.exists(counter_path):
            return None
        return int(phlsys_fs.read_text_file(counter_path).strip())

    def wait_one_or_more_cycles(self):
        assert self._has_enabled_count_cycles
        assert self._has_started_daemon
        while self.count_cycles() is None:
            time.sleep(1)
        start = self.count_cycles()
        count = start
        while count < start + 2:
            count = self.count_cycles()
            print(start, count)
            time.sleep(1)

    def run_once(self):
        return self('start', '--foreground', '--no-loop')

    def start_daemon(self):
        self._has_started_daemon = True
        return self('start')

    def stop_daemon(self):
        self._has_started_daemon = False
        return self('stop')

    @contextlib.contextmanager
    def daemon_context(self):
        self.start_daemon()
        try:
            yield
        finally:
            self.stop_daemon()

    def _read_log(self, name):
        log_path = '{}/var/log/{}'.format(self._root_dir, name)

        if os.path.isfile(log_path):
            return phlsys_fs.read_text_file(
                log_path)
        else:
            return ""

    def info_log(self):
        return self._read_log('info')

    def debug_log(self):
        return self._read_log('debug')

# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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
