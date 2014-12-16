"""Stop the arcyd instance for the current directory."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_stop
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import os
import time

import phlsys_fs
import phlsys_pid

import abdt_fs


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    pass


def process(unused_args):
    fs = abdt_fs.make_default_accessor()

    with fs.lockfile_context():
        pid = fs.get_pid_or_none()
        if pid is None or not phlsys_pid.is_running(pid):
            raise Exception("Arcyd is not running")

        killfile = 'var/command/killfile'
        phlsys_fs.write_text_file(killfile, '')

        if os.path.isfile(killfile):
            time.sleep(1)
            while os.path.isfile(killfile):
                print 'waiting for arcyd to remove killfile ..'
                time.sleep(1)

        # wait for Arcyd to not be running
        if phlsys_pid.is_running(pid):
            time.sleep(1)
            while phlsys_pid.is_running(pid):
                print 'waiting for arcyd to exit'
                time.sleep(1)


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
