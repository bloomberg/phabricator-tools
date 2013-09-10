"""Process the arguments for a single repository and execute."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_processargs
#
# Public Functions:
#   setup_parser
#   setup_repo_arg_parser
#   configure_sendmail
#   setup_sigterm_handler
#   make_exception_message_handler
#   make_exception_delay_handler
#   get_retry_delays
#   run_once
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import contextlib
import datetime
import logging
import platform
import signal
import sys
import traceback

import phlmail_sender
import phlsys_conduit
import phlsys_fs
import phlsys_pluginmanager
import phlsys_sendmail
import phlsys_strtotime
import phlsys_subprocess
import phlsys_traceback
import phlsys_tryloop

import abdmail_mailer
import abdt_conduit
import abdt_git
import abdt_reporeporter

import abdi_processrepo


def setup_parser(parser):
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


def setup_repo_arg_parser(parser):

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
        '--review-url-format',
        metavar="STRING",
        type=str,
        help="e.g. 'http://my.phabricator/{review}'")

    parser.add_argument(
        '--branch-url-format',
        metavar="STRING",
        type=str,
        help="e.g. 'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}'")

    parser.add_argument(
        '--try-touch-path',
        metavar="PATH",
        type=str,
        required=True,
        help="file to touch when trying to update a repo")

    parser.add_argument(
        '--ok-touch-path',
        metavar="PATH",
        type=str,
        required=True,
        help="file to touch when successfully updated a repo")

    parser.add_argument(
        "--plugins",
        metavar="MODULE_NAME",
        nargs="+",
        type=str,
        default=[],
        required=False,
        help="List the plugins to be loaded. MODULE_NAME must be present "
        "in /testbed/plugins/ directory as this feature is WIP.")

    parser.add_argument(
        "--trusted-plugins",
        metavar="MODULE_NAME",
        nargs="+",
        type=str,
        default=[],
        required=False,
        help="List the trusted plugins to be loaded. MODULE_NAME must be "
        "present in /testbed/plugins/ directory as this feature is WIP."
        "See /testbed/plugins/README.md for detail about trusted-plugins")


def configure_sendmail(args):
    if args.sendmail_binary:
        phlsys_sendmail.Sendmail.set_default_binary(
            args.sendmail_binary)

    if args.sendmail_type:
        phlsys_sendmail.Sendmail.set_default_params_from_type(
            args.sendmail_type)


# XXX: belongs in phlsys somewhere
def setup_sigterm_handler():
    def HandleSigterm(unused1, unused2):
        # raises 'SystemExit' exception, which will allow us to clean up
        sys.exit(1)
    signal.signal(signal.SIGTERM, HandleSigterm)


def _send_mail(mailsender, emails, uname, subject, tb, body_prefix, message):
    body = uname + "\n" + tb
    body += str(body_prefix)
    body += str(message)
    print body
    mailsender.send(
        subject=str(subject),
        message=body,
        to_addresses=emails)


def make_exception_message_handler(args, subject, body_prefix):
    uname = str(platform.uname())
    emails = args.sys_admin_emails

    mailsender = phlmail_sender.MailSender(
        phlsys_sendmail.Sendmail(),
        "arcyd@" + platform.node())

    def msg_exception(message):
        tb = traceback.format_exc()
        _send_mail(
            mailsender, emails, uname, subject, tb, body_prefix, message)

        # now risk trying to make a more detailed exception mail
        # (experimental, may fail)
        tb = phlsys_traceback.format_exc()
        _send_mail(
            mailsender, emails, uname, subject, tb, body_prefix, message)

    return msg_exception


def make_exception_delay_handler(args):
    return make_exception_message_handler(
        args,
        "arcyd paused with exception",
        "will wait: ")


def get_retry_delays():
    strToTime = phlsys_strtotime.duration_string_to_time_delta
    retry_delays = [strToTime(d) for d in ["10 minutes", "1 hours"]]
    return retry_delays


def run_once(args, out):

    reporter = abdt_reporeporter.RepoReporter(
        args.repo_desc,
        args.review_url_format,
        args.branch_url_format,
        abdt_reporeporter.SharedFileDictOutput(args.try_touch_path),
        abdt_reporeporter.SharedFileDictOutput(args.ok_touch_path))

    with contextlib.closing(reporter):
        _run_once(args, out, reporter)


def _run_once(args, out, reporter):

    sender = phlmail_sender.MailSender(
        phlsys_sendmail.Sendmail(), args.arcyd_email)

    mailer = abdmail_mailer.Mailer(
        sender,
        [args.admin_email],
        args.repo_desc,
        args.instance_uri)  # TODO: this should be a URI for users not conduit

    pluginManager = phlsys_pluginmanager.PluginManager(
        args.plugins, args.trusted_plugins)

    # prepare delays in the event of trouble when fetching or connecting
    # TODO: perhaps this policy should be decided higher-up
    delays = [
        datetime.timedelta(seconds=1),
        datetime.timedelta(seconds=1),
        datetime.timedelta(seconds=10),
        datetime.timedelta(seconds=10),
        datetime.timedelta(seconds=100),
        datetime.timedelta(seconds=100),
        datetime.timedelta(seconds=1000),
    ]

    # log.error if we get an exception when fetching
    def on_tryloop_exception(e, delay):
        reporter.on_tryloop_exception(e, delay)
        logging.error(str(e) + "\nwill wait " + str(delay))

    def prune_and_fetch():
        phlsys_subprocess.run_commands("git remote prune origin")
        phlsys_subprocess.run_commands("git fetch")

    with phlsys_fs.chdir_context(args.repo_path):
        out.display("fetch (" + args.repo_desc + "): ")
        phlsys_tryloop.try_loop_delay(
            prune_and_fetch,
            delays,
            onException=on_tryloop_exception)

    # XXX: until conduit refreshes the connection, we'll suffer from
    #      timeouts; reduce the probability of this by using a new
    #      conduit each time.

    # create an array so that the 'connect' closure binds to the 'conduit'
    # variable as we'd expect, otherwise it'll just modify a local variable
    # and this 'conduit' will remain 'None'
    # XXX: we can do better in python 3.x (nonlocal?)
    conduit = [None]

    def connect():
        # nonlocal conduit # XXX: we'll rebind in python 3.x, instead of array
        conduit[0] = phlsys_conduit.Conduit(
            args.instance_uri,
            args.arcyd_user,
            args.arcyd_cert,
            https_proxy=args.https_proxy)

    phlsys_tryloop.try_loop_delay(
        connect, delays, onException=on_tryloop_exception)

    out.display("process (" + args.repo_desc + "): ")
    arcyd_conduit = abdt_conduit.Conduit(conduit[0])

    branch_url_callable = None
    if args.branch_url_format:
        def make_branch_url(branch_name):
            return args.branch_url_format.format(branch=branch_name)
        branch_url_callable = make_branch_url

    arcyd_clone = abdt_git.Clone(
        args.repo_path, "origin", args.repo_desc, branch_url_callable)
    branches = arcyd_clone.get_managed_branches()

    try:
        abdi_processrepo.process_branches(
            branches,
            arcyd_conduit,
            mailer,
            pluginManager,
            reporter)
    except Exception:
        reporter.on_traceback(traceback.format_exc())
        raise

    reporter.on_completed()


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
