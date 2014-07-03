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

import phlsys_daemonize
import phlsys_pid
import phlsys_signal

import abdi_processrepos
import abdi_repoargs
import abdt_fs


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

    abdi_processrepos.process(args, repo_configs)


# -----------------------------------------------------------------------------
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
# ------------------------------ END-OF-FILE ----------------------------------
