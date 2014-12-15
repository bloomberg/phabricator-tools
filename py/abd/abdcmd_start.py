"""Start the arcyd instance for the current directory, if not already going."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_start
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

import argparse
import logging
import logging.handlers
import time

import phlsys_daemonize
import phlsys_multiprocessing
import phlsys_pid
import phlsys_signal

import abdi_processrepos
import abdi_repoargs
import abdt_fs

_LOGGER = logging.getLogger(__name__)


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--foreground',
        '-f',
        action='store_true',
        help="supply this argument to run arcyd interactively in the "
             "foreground")
    parser.add_argument(
        '--no-loop',
        action='store_true',
        help="supply this argument to only process each repo once then exit")


def process(args):
    # exit gracefully if this process is killed
    phlsys_signal.set_exit_on_sigterm()

    fs = abdt_fs.make_default_accessor()

    with fs.lockfile_context():
        pid = fs.get_pid_or_none()
        if pid is not None and phlsys_pid.is_running(pid):
            raise Exception("already running")

        if not args.foreground:
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

        if args.no_loop:
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


def _setup_logger(fs):
    # log DEBUG+ and INFO+ to separate files
    info_handler = logging.FileHandler(fs.layout.log_info)
    info_handler.setLevel(logging.INFO)

    # pychecker makes us do this, it won't recognise that logging.handlers is a
    # thing
    lg = logging
    debug_handler = lg.handlers.RotatingFileHandler(
        fs.layout.log_debug,
        maxBytes=10 * 1024 * 1024,
        backupCount=10)

    debug_handler.setLevel(logging.DEBUG)
    logfmt = '%(asctime)s UTC: %(levelname)s: (%(processName)-11s) %(message)s'
    formatter = logging.Formatter(logfmt)
    logging.Formatter.converter = time.gmtime
    info_handler.setFormatter(formatter)
    debug_handler.setFormatter(formatter)
    logging.getLogger().addHandler(info_handler)
    logging.getLogger().addHandler(debug_handler)
    logging.getLogger().setLevel(logging.DEBUG)


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
