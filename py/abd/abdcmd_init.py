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
from __future__ import division
from __future__ import print_function

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
    parser.add_argument(
        '--external-report-command',
        metavar="PATH",
        type=str,
        default=None,
        help="path to an external reporter to send monitoring info to, "
             "will be called like so: $REPORTER <<json report object>>")


def process(args):
    fs = abdt_fs.initialise_here()

    config = _DEFAULT_CONFIG.format(
        arcyd_email=args.arcyd_email,
        sys_admin_emails=' '.join(args.sys_admin_emails),
        sendmail_binary=args.sendmail_binary,
        sendmail_type=args.sendmail_type,
        sleep_secs=args.sleep_secs)

    if args.external_report_command:
        config += "\n--external-report-command\n{}".format(
            args.external_report_command)

    print(config)

    fs.create_root_config(config)


# -----------------------------------------------------------------------------
# Copyright (C) 2014-2015 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
