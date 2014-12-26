"""Create a new revision in differential.

you can use the 'revision id' output from this command as input to the
'arcyon update-revision' command.

usage examples:
    create a new revision by piping in a diff:
    $ diff -u file1 file2 | arcyon create-revision -t title -p plan -f -
    Created a new revision '99', you can visit it at this URL:
      http://127.0.0.1/D99

    create a new revision from diff 1, print id only (for scripting):
    $ arcyon create-revision -d 1 -t 'title' -p 'test plan' --format-id
    99

    create a new revision from diff 1, add a reviewer and a cc:
    $ arcyon create-revision -d 1 -t what -p test -r reviewer -c cc --format-id
    99

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_createrevision
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

import argparse

import phlcon_differential
import phlcon_user
import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    diffsrc_group = parser.add_argument_group(
        'Diff arguments',
        'Mutually exclusive, one is required')
    diffsrc = diffsrc_group.add_mutually_exclusive_group(required=True)
    req = parser.add_argument_group(
        'Required revision arguments',
        'Phabricator requires that you supply both of these')
    opt = parser.add_argument_group(
        'Optional revision arguments',
        'You can supply these later via the web interface if you wish')
    output_group = parser.add_argument_group(
        'Output format arguments',
        'Mutually exclusive, defaults to "--format-summary"')
    output = output_group.add_mutually_exclusive_group()

    diffsrc.add_argument(
        '--diff-id',
        metavar='INT',
        help='the id of the diff to create the file from, this could be '
             'the output from a "arcyon raw-diff" call',
        type=int)
    diffsrc.add_argument(
        '--raw-diff-file',
        '-f',
        help='the file to read the diff from, use \'-\' for stdin',
        metavar='FILE',
        type=argparse.FileType('r'))

    req.add_argument(
        '--title',
        '-t',
        metavar='TEXT',
        required=True,
        help='a short description of the changes to review',
        type=str)
    req.add_argument(
        '--test-plan',
        '-p',
        metavar='TEXT',
        required=True,
        help='how you tested your changes and how the reviewer'
             'can verify them',
        type=str)

    opt.add_argument(
        '--summary',
        '-s',
        metavar='TEXT',
        help='a longer summary of the changes to review',
        type=str)
    opt.add_argument(
        '--reviewers',
        '-r',
        nargs="*",
        metavar='USER',
        help='a list of reviewer usernames',
        type=str)
    opt.add_argument(
        '--ccs',
        '-c',
        nargs="*",
        metavar='USER',
        help='a list of usernames to cc on the review',
        type=str)

    output.add_argument(
        '--format-summary',
        action='store_true',
        help='will print a human-readable summary of the result.')
    output.add_argument(
        '--format-id',
        action='store_true',
        help='will print just the id of the new revision, for scripting.')
    output.add_argument(
        '--format-url',
        action='store_true',
        help='will print just the url of the new revision, for scripting.')

#   parser.add_argument(
#       '--deps', '--depends-on',
#       nargs="*",
#       metavar='ID',
#       type=int)

    phlsys_makeconduit.add_argparse_arguments(parser)


def process(args):
    conduit = phlsys_makeconduit.make_conduit(
        args.uri, args.user, args.cert, args.act_as_user)

    # create a new diff if we need to
    if args.diff_id:
        diff_id = args.diff_id
    else:
        d = {'diff': args.raw_diff_file.read()}
        diff_id = conduit("differential.createrawdiff", d)["id"]

    fields = {}

    MessageFields = phlcon_differential.MessageFields

    if args.reviewers:
        fields[MessageFields.reviewer_phids] = args.reviewers
    if args.ccs:
        fields[MessageFields.cc_phids] = args.ccs

    # conduit expects PHIDs not plain usernames
    user_phids = phlcon_user.UserPhidCache(conduit)
    for users in fields.itervalues():
        user_phids.add_hint_list(users)
    for key in fields.iterkeys():
        fields[key] = [user_phids.get_phid(u) for u in fields[key]]

    fields[MessageFields.title] = args.title
    fields[MessageFields.test_plan] = args.test_plan
    if args.summary:
        fields[MessageFields.summary] = args.summary

    d = {'diffid': diff_id, 'fields': fields}

    result = conduit("differential.createrevision", d)

    if args.format_id:
        print(result["revisionid"])
    elif args.format_url:
        print(result["uri"])
    else:  # args.format_summary:
        print((
            "Created a new revision '{rev_id}', you can view it at this URL:\n"
            "  {url}"
        ).format(
            rev_id=result["revisionid"],
            url=result["uri"]))


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
