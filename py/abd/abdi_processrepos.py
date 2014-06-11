"""Setup to process multiple repos."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_processrepos
#
# Public Functions:
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import os

import phlsys_sendmail

import abdt_arcydreporter
import abdt_exhandlers
import abdt_logging
import abdt_shareddictoutput

import abdi_processrepolist


def setupParser(parser):
    parser.add_argument(
        '--arcyd-email',
        metavar="EMAIL",
        type=str,
        required=True,
        help="email address for arcyd to send messages from")
    parser.add_argument(
        '--sys-admin-emails',
        metavar="EMAIL",
        nargs="+",
        type=str,
        required=True,
        help="email addresses to send important system events to")
    parser.add_argument(
        '--sendmail-binary',
        metavar="PROGRAM",
        type=str,
        default="sendmail",
        help="program to send the mail with (e.g. sendmail, catchmail)")
    parser.add_argument(
        '--sendmail-type',
        metavar="TYPE",
        type=str,
        default="sendmail",
        help="type of program to send the mail with (sendmail, catchmail), "
        "this will affect the parameters that Arycd will use.")
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
        '--io-log-file',
        metavar="PATH",
        type=str,
        default=None,
        help="filename of the io log file.")
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
    parser.add_argument(
        '--external-error-logger',
        metavar="PATH",
        type=str,
        default=None,
        help="path to an external logger to send errors to, will be called "
             "like so: $LOGGER '<<identifier>>' '<<full details>>'")


def process(args, repo_config_path_list):

    if args.sendmail_binary:
        phlsys_sendmail.Sendmail.set_default_binary(
            args.sendmail_binary)

    if args.sendmail_type:
        phlsys_sendmail.Sendmail.set_default_params_from_type(
            args.sendmail_type)

    reporter_data = abdt_shareddictoutput.ToFile(args.status_path)
    reporter = abdt_arcydreporter.ArcydReporter(
        reporter_data, args.arcyd_email, args.io_log_file)

    if args.external_error_logger:
        full_path = os.path.abspath(args.external_error_logger)
        reporter.set_external_system_error_logger(full_path)

    on_exception = abdt_exhandlers.make_exception_message_handler(
        args.sys_admin_emails,
        reporter,
        None,
        "arcyd stopped with exception",
        "")

    arcyd_reporter_context = abdt_logging.arcyd_reporter_context
    with contextlib.closing(reporter), arcyd_reporter_context(reporter):
        _processrepolist(args, repo_config_path_list, reporter, on_exception)


def _processrepolist(args, repo_config_path_list, reporter, on_exception):
    try:
        abdi_processrepolist.do(
            repo_config_path_list,
            args.sys_admin_emails,
            args.kill_file,
            args.reset_file,
            args.pause_file,
            args.sleep_secs,
            args.no_loop,
            reporter)
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


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
