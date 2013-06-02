"""Process the arguments for a single repository and execute."""

import datetime
import logging

import abdi_processrepo
import phlsys_sendmail
import phlmail_sender
import abdmail_mailer
import phlsys_conduit
import phlsys_fs
import phlsys_subprocess
import phlsys_tryloop


def run_once(args, out):
    sender = phlmail_sender.MailSender(
        phlsys_sendmail.Sendmail(), args.arcyd_email)
    mailer = abdmail_mailer.Mailer(
        sender,
        [args.admin_email],
        args.repo_desc,
        args.instance_uri)  # TODO: this should be a URI for users not conduit

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
    def on_exception(e, delay):
        logging.error(str(e) + "\nwill wait " + str(delay))

    if args.try_touch_path:
        try:
            # TODO: don't rely on the touch command
            phlsys_subprocess.run("touch", args.try_touch_path)
        except Exception:
            pass  # XXX: we don't care atm, later log this

    with phlsys_fs.chdir_context(args.repo_path):
        out.display("fetch (" + args.repo_desc + "): ")
        phlsys_tryloop.try_loop_delay(
            lambda: phlsys_subprocess.run_commands("git fetch -p"),
            delays,
            onException=on_exception)

    # XXX: until conduit refreshes the connection, we'll suffer from
    #      timeouts; reduce the probability of this by using a new
    #      conduit each time.

    # create an array so that the 'connect' closure binds to the 'conduit'
    # variable as we'd expect, otherwise it'll just modify a local variable
    # and this 'conduit' will remain 'None'
    # XXX: we can do better in python 3.x
    conduit = [None]

    def connect():
        #nonlocal conduit # XXX: we'll rebind in python 3.x, instead of array
        conduit[0] = phlsys_conduit.Conduit(
            args.instance_uri,
            args.arcyd_user,
            args.arcyd_cert,
            https_proxy=args.https_proxy)

    phlsys_tryloop.try_loop_delay(connect, delays, onException=on_exception)

    out.display("process (" + args.repo_desc + "): ")
    abdi_processrepo.processUpdatedRepo(
        conduit[0], args.repo_path, "origin", mailer)

    if args.ok_touch_path:
        try:
            # TODO: don't rely on the touch command
            phlsys_subprocess.run("touch", args.ok_touch_path)
        except Exception:
            pass  # XXX: we don't care atm, later log this


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
