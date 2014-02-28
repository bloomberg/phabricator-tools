"""Create a new arcyd instance in working dir, with backing git repository."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_init
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

import abdt_fs

_DEFAULT_CONFIG = """
--arcyd-email
{arcyd_email}
--sys-admin-emails
{sys_admin_emails}
--sendmail-binary
{sendmail_binary}
--sendmail-type
{sendmail_type}
--status-path
var/status/arcyd_status.json
--io-log-file
var/log/git-phab-writes.log
--kill-file
var/command/killfile
--sleep-secs
{sleep_secs}
""".strip()


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--arcyd-email',
        metavar="EMAIL",
        type=str,
        required=True,
        help="email address for arcyd to send messages from")
    parser.add_argument(
        '--sys-admin-emails',
        type=str,
        metavar='ADDR',
        nargs='+',
        default=['root@localhost'],
        help='list of email address to send mail to on system error.')
    parser.add_argument(
        '--sleep-secs',
        metavar="TIME",
        type=int,
        default=60,
        help="override time to wait between runs through the list")
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
        "this will affect the parameters that Arcyd will use.")


def process(args):
    fs = abdt_fs.initialise_here()

    config = _DEFAULT_CONFIG.format(
        arcyd_email=args.arcyd_email,
        sys_admin_emails=' '.join(args.sys_admin_emails),
        sendmail_binary=args.sendmail_binary,
        sendmail_type=args.sendmail_type,
        sleep_secs=args.sleep_secs)

    fs.create_root_config(config)


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
