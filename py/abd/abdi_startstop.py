"""Daemon startup and shutdown helpers."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_startstop
#
# Public Functions:
#   start_arcyd
#   stop_arcyd
#   stop_arcyd_pid
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import logging
import logging.handlers
import os
import time

import phlsys_compressedlogging
import phlsys_daemonize
import phlsys_fs
import phlsys_multiprocessing
import phlsys_pid
import phlsys_signal
import phlsys_verboseerrorfilter

import abdt_fs

import abdi_processrepos
import abdi_repoargs

_LOGGER = logging.getLogger(__name__)


def start_arcyd(daemonize=True, loop=True, restart=False):
    # exit gracefully if this process is killed
    phlsys_signal.set_exit_on_sigterm()

    fs = abdt_fs.make_default_accessor()

    with fs.lockfile_context():
        pid = fs.get_pid_or_none()
        if pid is not None and phlsys_pid.is_running(pid):
            if restart:
                stop_arcyd_pid(pid)
            else:
                raise Exception("already running")

        if daemonize:
            phlsys_daemonize.do(
                stdout_path=fs.layout.stdout,
                stderr_path=fs.layout.stderr)

        # important that we do this *after* daemonizing
        pid = phlsys_pid.get()
        fs.set_pid(pid)

        parser = argparse.ArgumentParser()
        params = []

        for line in open(fs.layout.root_config):
            params.append(line.strip())

        if not loop:
            params.append('--no-loop')

        repo_configs = abdi_repoargs.parse_config_file_list(
            fs.repo_config_path_list())

        abdi_processrepos.setupParser(parser)
        args = parser.parse_args(params)

    def logger_config():
        _setup_logger(fs)

    with phlsys_multiprocessing.logging_context(logger_config):
        _LOGGER.debug("start with args: {}".format(args))
        _LOGGER.info("arcyd started")
        try:
            abdi_processrepos.process(args, repo_configs)
        finally:
            _LOGGER.info("arcyd stopped")


def stop_arcyd():
    fs = abdt_fs.make_default_accessor()

    with fs.lockfile_context():
        pid = fs.get_pid_or_none()
        if pid is None or not phlsys_pid.is_running(pid):
            raise Exception("Arcyd is not running")
        stop_arcyd_pid(pid)


def stop_arcyd_pid(pid):
    killfile = 'var/command/killfile'
    phlsys_fs.write_text_file(killfile, '')

    if os.path.isfile(killfile):
        time.sleep(1)
        while os.path.isfile(killfile):
            print('waiting for arcyd to remove killfile ..')
            time.sleep(1)

    # wait for Arcyd to not be running
    if phlsys_pid.is_running(pid):
        time.sleep(1)
        while phlsys_pid.is_running(pid):
            print('waiting for arcyd to exit')
            time.sleep(1)


def _setup_logger(fs):
    # log DEBUG+, INFO+ and ERROR+ to separate files

    # pychecker makes us do this, it won't recognise that logging.handlers is a
    # thing
    lg = logging

    error_handler = lg.handlers.RotatingFileHandler(
        fs.layout.log_error,
        maxBytes=10 * 1024 * 1024,
        backupCount=10)
    error_handler.setLevel(logging.ERROR)

    info_handler = lg.handlers.RotatingFileHandler(
        fs.layout.log_info,
        maxBytes=10 * 1024 * 1024,
        backupCount=10)
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(phlsys_verboseerrorfilter.getFilter())

    debug_handler = phlsys_compressedlogging.CompressedRotatingFileHandler(
        fs.layout.log_debug,
        maxBytes=50 * 1024 * 1024,
        backupCount=10)
    debug_handler.setLevel(logging.DEBUG)

    logfmt = '%(asctime)s UTC: %(levelname)s: (%(processName)-11s) %(message)s'
    formatter = logging.Formatter(logfmt)
    logging.Formatter.converter = time.gmtime
    error_handler.setFormatter(formatter)
    info_handler.setFormatter(formatter)
    debug_handler.setFormatter(formatter)
    logging.getLogger().addHandler(error_handler)
    logging.getLogger().addHandler(info_handler)
    logging.getLogger().addHandler(debug_handler)


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
