"""Command to process a single repository."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_single
#
# Public Classes:
#   DelayedRetrySleepOperation
#    .do
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import functools
import time

import abdi_processargs
import phlsys_scheduleunreliables
import phlsys_statusline


def getFromfilePrefixChars():
    return '@'


def setupParser(parser):

    parser.add_argument(
        '--instance-uri',
        metavar="URI",
        type=str,
        required=True,
        help="instance to connect to, e.g. http://127.0.0.1")

    parser.add_argument(
        '--arcyd-user',
        metavar="USER",
        type=str,
        required=True,
        help="username for Arcyd to use")

    parser.add_argument(
        '--arcyd-cert',
        metavar="CERT",
        type=str,
        required=True,
        help="Phabricator Conduit API certificate to use, this is the "
        "value that you will find in your user account in Phabricator "
        "at: http://your.server.example/settings/panel/conduit/. "
        "It can also be found in ~/.arcrc.")

    parser.add_argument(
        '--arcyd-email',
        metavar="FROM",
        type=str,
        required=True,
        help="email address for Arcyd to send mails from")

    parser.add_argument(
        '--admin-email',
        metavar="TO",
        type=str,
        required=True,
        help="email address to send important system events to")

    parser.add_argument(
        '--repo-desc',
        metavar="DESC",
        type=str,
        required=True,
        help="description to use in emails")

    parser.add_argument(
        '--repo-path',
        metavar="PATH",
        type=str,
        required=True,
        help="path to the repository on disk")

    parser.add_argument(
        '--https-proxy',
        metavar="PROXY",
        type=str,
        help="proxy to use, if necessary")

    parser.add_argument(
        '--sleep-secs',
        metavar="TIME",
        type=int,
        default=60,
        help="time to wait between fetches")

    parser.add_argument(
        '--try-touch-path',
        metavar="PATH",
        type=str,
        help="file to touch when trying to update a repo")

    parser.add_argument(
        '--ok-touch-path',
        metavar="PATH",
        type=str,
        help="file to touch when successfully updated a repo")


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
    out = phlsys_statusline.StatusLine()

    # TODO: test write access to repo here

    operations = []

    operations.append(
        phlsys_scheduleunreliables.DelayedRetryNotifyOperation(
            functools.partial(abdi_processargs.run_once, args, out),
            list(retry_delays),  # make a copy to be sure
            on_exception_delay))

    operations.append(
        DelayedRetrySleepOperation(
            out, args.sleep_secs))

    phlsys_scheduleunreliables.loop_forever(operations)


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
