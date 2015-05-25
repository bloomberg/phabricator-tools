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
from __future__ import division
from __future__ import print_function

import argparse

import phlsys_conduit
import phlsys_makeconduit
import phlsys_subcommand

import aoncmd_comment
import aoncmd_commentinline
import aoncmd_createrevision
import aoncmd_getdiff
import aoncmd_gitdiffhelper
import aoncmd_paste
import aoncmd_query
import aoncmd_rawdiff
import aoncmd_showconfig
import aoncmd_taskcreate
import aoncmd_taskquery
import aoncmd_taskupdate
import aoncmd_updaterevision

_USAGE_EXAMPLES = """
usage examples:

    to display the config that arcyon will use:
    $ arcyon show-config

    to display help on the show-config sub-command:
    $ arcyon show-config --help

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

    to create a diff to pass to arcyon, from within a git repository:
    $ arcyon git-diff-helper base head
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
    phlsys_subcommand.setup_parser(
        "comment-inline", aoncmd_commentinline, subparsers)
    phlsys_subcommand.setup_parser("raw-diff", aoncmd_rawdiff, subparsers)
    phlsys_subcommand.setup_parser(
        "create-revision", aoncmd_createrevision, subparsers)
    phlsys_subcommand.setup_parser(
        "update-revision", aoncmd_updaterevision, subparsers)
    phlsys_subcommand.setup_parser("get-diff", aoncmd_getdiff, subparsers)
    phlsys_subcommand.setup_parser("paste", aoncmd_paste, subparsers)
    phlsys_subcommand.setup_parser(
        "task-create", aoncmd_taskcreate, subparsers)
    phlsys_subcommand.setup_parser(
        "task-update", aoncmd_taskupdate, subparsers)
    phlsys_subcommand.setup_parser(
        "task-query", aoncmd_taskquery, subparsers)

    phlsys_subcommand.setup_parser(
        "git-diff-helper", aoncmd_gitdiffhelper, subparsers)

    args = parser.parse_args()

    try:
        return args.func(args)
    except phlsys_conduit.ConduitException as e:

        # pychecker won't let us pass 'e' in as a keyword argument, so we
        # address it as parameter 0 instead
        fmt = (
            "ERROR ({0.error}): "
            "Phabricator {0.method} could not perform request:\n"
            "{0.errormsg}"
        )
        message = fmt.format(e)

        print(message)
        print()
        return 1
    except phlsys_makeconduit.InsufficientInfoException as e:
        print("ERROR - insufficient information")
        print(e)
        print()
        print("N.B. you may also specify uri, user or cert directly like so:")
        print("  --uri URI           address of phabricator instance")
        print("  --user USERNAME     username of user to connect as")
        print("  --cert CERTIFICATE  certificate for user Phabrictor account")
        return 1


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
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
