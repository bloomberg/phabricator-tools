"""Process the arguments for a single repository and execute."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_processargs
#
# Public Functions:
#   run_once
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import contextlib
import datetime
import logging

import abdi_processrepo
import abdmail_mailer
import phlmail_sender
import phlsys_conduit
import phlsys_fs
import phlsys_pluginmanager
import phlsys_sendmail
import phlsys_subprocess
import phlsys_tryloop

import abdt_conduit
import abdt_git
import abdt_reporeporter


def run_once(args, out):

    reporter = abdt_reporeporter.RepoReporter(
        args.try_touch_path, args.ok_touch_path)

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

    pluginManager = phlsys_pluginmanager.PluginManager(args.plugins)

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

    with phlsys_fs.chdir_context(args.repo_path):
        out.display("fetch (" + args.repo_desc + "): ")
        phlsys_tryloop.try_loop_delay(
            lambda: phlsys_subprocess.run_commands("git fetch -p"),
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
    arcyd_clone = abdt_git.Clone(args.repo_path, "origin")
    branches = arcyd_clone.get_managed_branches()

    try:
        abdi_processrepo.process_branches(
            branches,
            arcyd_conduit,
            mailer,
            pluginManager,
            reporter)
    except Exception as e:
        reporter.on_exception(e)
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
