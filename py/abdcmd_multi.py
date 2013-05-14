#!/usr/bin/env python
# encoding: utf-8

"""Command to process multiple repos."""

import argparse
import functools
import time

import abdcmd_single
import abdi_processargs
import phlsys_statusline
import phlsys_scheduleunreliables


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--repo-configs',
        metavar="N",
        action='append',
        nargs='+',
        type=str,
        help="files to load configuration from, prefix with @")
    parser.add_argument(
        '--sleep-secs',
        metavar="TIME",
        type=int,
        default=60,
        help="time to wait between runs through the list")


class DelayedRetrySleepOperation(object):
    def __init__(self, out, secs):
        self._out = out
        self._secs = secs

    def do(self):
        sleep_remaining = self._secs
        while sleep_remaining > 0:
            self._out.display("sleep (" + str(sleep_remaining) + " seconds) ")
            time.sleep(1)
            sleep_remaining -= 1
        return True


def process(args, retry_delays, on_exception_delay):
    repos = []
    for repo in args.repo_configs:
        # TODO: we should not depend on another command like this
        parser = argparse.ArgumentParser(
            fromfile_prefix_chars=abdcmd_single.getFromfilePrefixChars())
        abdcmd_single.setupParser(parser)
        repo_args = parser.parse_args(repo)
        repos.append(repo_args)

    out = phlsys_statusline.StatusLine()

    # TODO: test write access to repos here

    operations = []
    for repo in repos:
        operation = phlsys_scheduleunreliables.DelayedRetryNotifyOperation(
            functools.partial(abdi_processargs.run_once, repo, out),
            list(retry_delays),  # make a copy to be sure
            on_exception_delay)
        operations.append(operation)

    operations.append(
        DelayedRetrySleepOperation(
            out, args.sleep_secs))

    phlsys_scheduleunreliables.loopForever(operations)


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
