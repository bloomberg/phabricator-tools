"""Command to process multiple repos."""

import argparse
import functools
import time
import os

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
        f()
    except ResetFileException as e:
        on_exception_delay(None)
        try:
            os.remove(e.path)
        except:
            on_exception_delay(None)


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

    def on_pause():
        on_exception_delay("until_file_removed")

    operations.append(
        FileCheckOperation(
            args.kill_file,
            args.reset_file,
            args.pause_file,
            on_pause))

    operations.append(
        DelayedRetrySleepOperation(
            out, args.sleep_secs))

    def loopForever():
        phlsys_scheduleunreliables.loopForever(list(operations))

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
