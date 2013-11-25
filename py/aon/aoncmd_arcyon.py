"""Arcyon - util to interact with Conduit API from the command-line.

Intended to make the Conduit API easily accessible and discoverable from a
dedicated command-line tool. This should make it easier to write shell scripts
which extend Phabricator.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_arcyon
#
# Public Functions:
#   main
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import argparse

import phlsys_makeconduit
import phlsys_subcommand

import aoncmd_comment
import aoncmd_createrevision
import aoncmd_getdiff
import aoncmd_paste
import aoncmd_query
import aoncmd_rawdiff
import aoncmd_showconfig
import aoncmd_taskcreate
import aoncmd_updaterevision

_USAGE_EXAMPLES = """
usage examples:

    to display the config that arcyon will use:
    $ arcyon show-config

    to list revisions where you are the author:
    $ arcyon query --author-me

    to list open revisions where you are the author:
    $ arcyon query --author-me --status-type open

    to list revisions that are old and open:
    $ arcyon query --status-type open --min-update-age "2 weeks"

    to comment on revision '1':
    $ arcyon comment 1 -m 'hello'

    to comment on every revision:
    $ arcyon query --format-type ids | arcyon comment --ids-file - -m hello
    """


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    subparsers = parser.add_subparsers()

    phlsys_subcommand.setup_parser(
        "show-config", aoncmd_showconfig, subparsers)
    phlsys_subcommand.setup_parser("query", aoncmd_query, subparsers)
    phlsys_subcommand.setup_parser("comment", aoncmd_comment, subparsers)
    phlsys_subcommand.setup_parser("raw-diff", aoncmd_rawdiff, subparsers)
    phlsys_subcommand.setup_parser(
        "create-revision", aoncmd_createrevision, subparsers)
    phlsys_subcommand.setup_parser(
        "update-revision", aoncmd_updaterevision, subparsers)
    phlsys_subcommand.setup_parser("get-diff", aoncmd_getdiff, subparsers)
    phlsys_subcommand.setup_parser("paste", aoncmd_paste, subparsers)
    phlsys_subcommand.setup_parser(
        "task-create", aoncmd_taskcreate, subparsers)

    args = parser.parse_args()

    try:
        return args.func(args)
    except phlsys_makeconduit.InsufficientInfoException as e:
        print "ERROR - insufficient information"
        print e
        print
        print "N.B. you may also specify uri, user or cert explicitly like so:"
        print "  --uri URI           address of phabricator instance"
        print "  --user USERNAME     username of user to connect as"
        print "  --cert CERTIFICATE  certificate for user Phabrictor account"
        return 1


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
