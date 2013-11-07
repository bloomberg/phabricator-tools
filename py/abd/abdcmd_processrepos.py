"""Command to process multiple repos."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_processrepos
#
# Public Classes:
#   DelayedRetrySleepOperation
#    .do
#   RefreshCachesOperation
#    .do
#   ResetFileException
#   FileCheckOperation
#    .do
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   tryHandleSpecialFiles
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import argparse
import contextlib
import functools
import os
import sys
import time

import phlsys_scheduleunreliables
import phlsys_statusline
import phlurl_watcher

import abdi_processargs
import abdt_arcydreporter
import abdt_logging
import abdt_shareddictoutput
import abdt_tryloop


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    abdi_processargs.setup_parser(parser)
    parser.add_argument(
        '--repo-configs',
        metavar="N",
        action='append',
        nargs='+',
        type=str,
        help="files to load configuration from, prefix with @")
    parser.add_argument(
        '--status-path',
        metavar="PATH",
        type=str,
        required=True,
        help="file to write status to")
    parser.add_argument(
        '--kill-file',
        metavar="NAME",
        type=str,
        help="filename to watch for, will stop operations safely if the file "
             "is detected.")
    parser.add_argument(
        '--pause-file',
        metavar="NAME",
        type=str,
        help="filename to watch for, will pause operations while the file is "
             "detected.")
    parser.add_argument(
        '--reset-file',
        metavar="NAME",
        type=str,
        help="filename to watch for, will reset operations if the file is "
             "detected and remove the file.")
    parser.add_argument(
        '--sleep-secs',
        metavar="TIME",
        type=int,
        default=60,
        help="time to wait between runs through the list")
    parser.add_argument(
        '--no-loop',
        action='store_true',
        help="supply this argument to only process each repo once then exit")


class DelayedRetrySleepOperation(object):

    def __init__(self, out, secs, reporter):
        self._out = out
        self._secs = secs
        self._reporter = reporter

    def do(self):
        sleep_remaining = self._secs
        self._reporter.start_sleep(sleep_remaining)
        while sleep_remaining > 0:
            self._out.display("sleep (" + str(sleep_remaining) + " seconds) ")
            self._reporter.update_sleep(sleep_remaining)
            time.sleep(1)
            sleep_remaining -= 1
        self._reporter.finish_sleep()
        return True


class RefreshCachesOperation(object):

    def __init__(self, conduits, url_watcher, reporter):
        super(RefreshCachesOperation, self).__init__()
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
                    "conduit-refresh",
                    conduit.describe())

        with self._reporter.tag_timer_context('refresh git watcher'):
            abdt_tryloop.critical_tryloop(
                self._url_watcher.refresh, 'git-snoop', '')

        self._reporter.finish_cache_refresh()
        return True


class ResetFileException(Exception):

    def __init__(self, path):
        self.path = path
        super(ResetFileException, self).__init__()


class FileCheckOperation(object):

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
            raise ResetFileException(self._reset_file)
        if self._pause_file and os.path.isfile(self._pause_file):
            if self._on_pause:
                self._on_pause()
            while os.path.isfile(self._pause_file):
                time.sleep(1)
        return True


def tryHandleSpecialFiles(f, on_exception_delay):
    try:
        return f()
    except ResetFileException as e:
        on_exception_delay(None)
        try:
            os.remove(e.path)
        except:
            on_exception_delay(None)


def process(args):

    abdi_processargs.setup_sigterm_handler()
    abdi_processargs.configure_sendmail(args)

    reporter_data = abdt_shareddictoutput.ToFile(args.status_path)
    reporter = abdt_arcydreporter.ArcydReporter(reporter_data)

    on_exception = abdi_processargs.make_exception_message_handler(
        args, reporter, None, "arcyd stopped with exception", "")

    arcyd_reporter_context = abdt_logging.arcyd_reporter_context
    with contextlib.closing(reporter), arcyd_reporter_context(reporter):

        try:
            _process(args, reporter)
        except BaseException:
            on_exception("Arcyd will now stop")
            print "stopping"
            raise

        if not args.no_loop:
            # we should never get here, raise and handle an exception if we do
            try:
                raise Exception("Arcyd stopped unexpectedly")
            except Exception:
                on_exception("Arcyd will now stop")


def _process(args, reporter):

    retry_delays = abdi_processargs.get_retry_delays()

    repos = []
    for repo in args.repo_configs:
        parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
        abdi_processargs.setup_repo_arg_parser(parser)
        repo_name = repo[0]  # oddly this comes to us as a list
        repo_name = repo_name[1:]  # strip off the '@' prefix
        repo_args = (repo_name, parser.parse_args(repo))
        repos.append(repo_args)

    out = phlsys_statusline.StatusLine()

    # TODO: test write access to repos here

    operations = []
    conduits = {}
    url_watcher = phlurl_watcher.Watcher()
    for repo, repo_args in repos:

        process_func = functools.partial(
            abdi_processargs.run_once,
            repo,
            repo_args,
            out,
            reporter,
            conduits,
            url_watcher)

        on_exception_delay = abdi_processargs.make_exception_delay_handler(
            args, reporter, repo)
        operation = phlsys_scheduleunreliables.DelayedRetryNotifyOperation(
            process_func,
            list(retry_delays),  # make a copy to be sure
            on_exception_delay)

        operations.append(operation)

    def on_pause():
        on_exception_delay = abdi_processargs.make_exception_delay_handler(
            args, reporter, None)
        on_exception_delay("until_file_removed")

    operations.append(
        FileCheckOperation(
            args.kill_file,
            args.reset_file,
            args.pause_file,
            on_pause))

    operations.append(
        DelayedRetrySleepOperation(
            out, args.sleep_secs, reporter))

    operations.append(
        RefreshCachesOperation(
            conduits, url_watcher, reporter))

    if args.no_loop:
        def process_once():
            return phlsys_scheduleunreliables.process_once(list(operations))

        new_ops = tryHandleSpecialFiles(process_once, on_exception_delay)
        if new_ops != set(operations):
            print 'ERROR: some operations failed'
            sys.exit(1)
    else:
        def loopForever():
            phlsys_scheduleunreliables.process_loop_forever(list(operations))

        while True:
            tryHandleSpecialFiles(loopForever, on_exception_delay)


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
