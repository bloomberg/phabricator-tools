"""Arcyd - daemon to watch git repos, create and land reviews automatically.

Intended to make it easy for large teams to start using Differential without
individual contributors needing to install and configure Arcanist.

Individual contributors are still free to use Arcanist if they wish, Arcyd
provides a zero-config layer over Git to get them started.

Arcyd does the following:
- watches for specially named branches and automatically creates revisions
- automatically updates revisions when the branch changes
- automatically lands revisions when they are approved

minimal user workflow:
    $ git checkout feature/mywork
    ~ commit some work on the branch ~
    $ git push origin feature/mywork:ph-review/mywork/master

    .. Arcyd see's the 'ph-review' branch and creates a review ..
    .. Reviewer accepts the change ..
    .. Arcyd squashes the 'ph-review' branch onto master and deletes it ..
"""

_USAGE_EXAMPLES = """
usage example:
    Using the example accounts baked into the 'phabricator-tools'
    vagrant/puppet installation. (see ./README)

    $ arcyd
    --system-admin-email systemadmin@server.test \\
    --sendmail-binary sendmail \\
    --sendmail-type sendmail \\
    single \\
    --instance-uri https://127.0.0.1/api/ \\
    --arcyd-user phab \\
    --arcyd-cert xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7\
ru3lrvafgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo\
2j3y2w6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5\
rpicdk3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf
    --arcyd-email phab-role-account@server.example \\
    --admin-email admin@server.example \\
    --repo-desc http://server.example/repo.git \\
    --sleep-duration 60

    You can also split the configuration across multiple files and combine them
    on the command-line or have them inherit from eachother.

    in localinstance.cfg:
        --instance-uri
        https://127.0.0.1/api/
        --arcyd-user
        phab
        --arcyd-cert
        <<paste-certificate-here>>

    in email.cfg:
        --arcyd-email
        phab-role-account@server.example
        --admin-email
        admin@server.example

    in repo1.cfg:
        --repo-desc
        http://server.example/repo.git
        --repo-path
        /path/to/repo

    to run arcyd:
    $ arcyd
    --system-admin-email systemadmin@server.test \\
    --sendmail-binary sendmail \\
    --sendmail-type sendmail \\
    single @localinstance.cfg @email.cfg @repo1.cfg

    or you can use inheritance, e.g. in repo2.cfg:
        @localinstance.cfg
        @email.cfg
        --repo-desc
        http://server.example/repo2.git
        --repo-path
        /path/to/repo

    to run arcyd:
    $ arcyd
    --system-admin-email systemadmin@server.test \\
    --sendmail-binary sendmail \\
    --sendmail-type sendmail \\
    single @localinstance.cfg @email.cfg @repo1.cfg
    """

import argparse
import platform
import signal
import sys
import traceback

import abdcmd_single
import abdcmd_multi
import phlmail_sender
import phlsys_sendmail
import phlsys_subcommand
import phlsys_strtotime


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

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
        required=True,
        help="program to send the mail with (e.g. sendmail, catchmail)")

    parser.add_argument(
        '--sendmail-type',
        metavar="TYPE",
        type=str,
        default="sendmail",
        required=True,
        help="type of program to send the mail with (sendmail, catchmail), "
        "this will affect the parameters that Arycd will use.")

    subparsers = parser.add_subparsers()

    phlsys_subcommand.setup_parser("single", abdcmd_single, subparsers)
    phlsys_subcommand.setup_parser("multi", abdcmd_multi, subparsers)

    args = parser.parse_args()

    uname = str(platform.uname())

    if args.sendmail_binary:
        phlsys_sendmail.Sendmail.set_default_binary(
            args.sendmail_binary)

    if args.sendmail_type:
        phlsys_sendmail.Sendmail.set_default_params_from_type(
            args.sendmail_type)

    mailsender = phlmail_sender.MailSender(
        phlsys_sendmail.Sendmail(),
        "arcyd@" + platform.node())

    # exit if we're stopped by SIGTERM
    def HandleSigterm(unused1, unused2):
        # raises 'SystemExit' exception, which will allow us to clean up
        sys.exit(1)
    signal.signal(signal.SIGTERM, HandleSigterm)

    strToTime = phlsys_strtotime.durationStringToTimeDelta
    retry_delays = [strToTime(d) for d in ["10 minutes", "1 hours"]]

    emails = args.sys_admin_emails

    def msgException(delay):
        message = uname + "\n" + traceback.format_exc()
        message += "\nwill wait:" + str(delay)
        print message
        mailsender.send(
            subject="arcyd paused with exception",
            message=message,
            to_addresses=emails)

    try:
        args.func(args, retry_delays, msgException)
    except:
        message = uname + "\n" + traceback.format_exc()
        print message
        mailsender.send(
            subject="arcyd stopped with exception",
            message=message,
            to_addresses=emails)
        sys.exit(1)

    mailsender.send(
        subject="arcyd stopped",
        message="",
        to_addresses=args.sys_admin_emails)


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
