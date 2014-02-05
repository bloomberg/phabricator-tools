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

import phlgit_commit
import phlsys_fs
import phlsys_git
import phlsys_subprocess

_DEFAULT_CONFIG = """
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

_README = """
This is an Arcyd repository.

Run 'arcyd --help' for options.
""".strip()

_VAR_README = """
In this directory all the repositories, logs and other run-time generated data
is stored.

It is safe to clean this directory when Arcyd is not running, you should save
any logs that you'd like to keep beforehand of course.

This is really a stand-in for using '/var' on the machine, this makes it
convenient to run arcyd where it can't be installed as root whilst keeping it
conceivable to move to a packaged install process later.
""".strip()

_VAR_REPO_README = """
This is where Arcyd keeps all the local clones of repositories that it is
managing.
""".strip()

_VAR_LOG_README = """
This is where Arcyd keeps all activity logs.
""".strip()

_VAR_STATUS_README = """
This is where Arcyd keeps all status information.
""".strip()

_VAR_COMMAND_README = """
This is where Arcyd looks for command files, e.g. to pause or stop.
""".strip()

_VAR_RUN_README = """
This is where Arcyd puts it's pidfile.
""".strip()


def getFromfilePrefixChars():
    return None


def setupParser(parser):
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
    phlsys_subprocess.run('git', 'init')
    repo = phlsys_git.Repo('.')

    # create filesystem hierarchy
    phlsys_fs.write_text_file('.arcydroot', 'this dir is an arcydroot')
    phlsys_fs.write_text_file('config', _DEFAULT_CONFIG.format(
        sys_admin_emails=' '.join(args.sys_admin_emails),
        sendmail_binary=args.sendmail_binary,
        sendmail_type=args.sendmail_type,
        sleep_secs=args.sleep_secs))
    phlsys_fs.write_text_file('README', _README)
    phlsys_fs.write_text_file('var/README', _VAR_README)
    phlsys_fs.write_text_file('var/repo/README', _VAR_REPO_README)
    phlsys_fs.write_text_file('var/log/README', _VAR_LOG_README)
    phlsys_fs.write_text_file('var/status/README', _VAR_STATUS_README)
    phlsys_fs.write_text_file('var/command/README', _VAR_COMMAND_README)
    phlsys_fs.write_text_file('var/run/README', _VAR_RUN_README)

    repo.call('add', '.')
    phlsys_fs.write_text_file('.gitignore', 'var\n')
    repo.call('add', '.')
    phlgit_commit.index(repo, 'Initialised new Arcyd instance')


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
