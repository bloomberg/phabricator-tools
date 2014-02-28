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
import os

import phlsys_pid

import abdi_processrepos
import abdt_fs


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--no-loop',
        action='store_true',
        help="supply this argument to only process each repo once then exit")


def _is_repo_config_path(x):
    return x.startswith('repo-') and x.endswith('.config')


def _list_repo_configs_in_workingdir():
    return [x for x in os.listdir('.') if _is_repo_config_path(x)]


def process(args):
    fs = abdt_fs.make_default_accessor()

    pid = fs.get_pid_or_none()
    if pid is not None and phlsys_pid.is_running(pid):
        raise Exception("already running")

    pid = phlsys_pid.get()
    fs.set_pid(pid)

    repo_configs = _list_repo_configs_in_workingdir()

    # XXX: hack this horribly by delegating everything to the 'process-repos'
    #      command
    parser = argparse.ArgumentParser()
    params = []

    for line in open(fs.layout.root_config):
        params.append(line.strip())

    if args.no_loop:
        params.append('--no-loop')

    for repo in repo_configs:
        params.append('--repo-configs')
        params.append('@' + repo)

    abdi_processrepos.setupParser(parser)
    args = parser.parse_args(params)
    abdi_processrepos.process(args)


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
