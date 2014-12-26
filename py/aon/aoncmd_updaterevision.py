"""Update an existing revision in differential.

Note:

    When updating an existing revision, you should submit a diff versus
    the original file. Otherwise the display in Differential may not be as you
    expect.

    e.g.

    You have 3 versions of your README file:
        README_original.txt
        README_update_1.txt
        README_update_2.txt

    You would like to create a review of these two updates in sequence,
    the correct way to do it is this:

    1. create the review with this diff:
       $ diff -u README_original.txt README_update_1.txt

    2. update the review with this diff:
       $ diff -u README_original.txt README_update_2.txt

Usage examples:

    update revision 99 by piping in a diff:
    $ diff -u file1 file2 | arcyon update-revision 99 fixes -f -
    99

    update revision 99 from diff 2:
    $ arcyon update-revision 99 'fix review issues' -d 2
    99

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_updaterevision
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

import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    diffsrc_group = parser.add_argument_group(
        'Diff arguments',
        'Mutually exclusive, one is required')
    diffsrc = diffsrc_group.add_mutually_exclusive_group(required=True)
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

    parser.add_argument(
        'revision_id',
        help='the id of the revision to update, e.g. the output from a '
             'previous "arcyon create-revision" command',
        type=str)

    parser.add_argument(
        'message',
        help='a short description of the update, this appears on the review '
             'page',
        type=str)

    output.add_argument(
        '--format-summary',
        action='store_true',
        help='will print a human-readable summary of the result.')
    output.add_argument(
        '--format-id',
        action='store_true',
        help='will print just the id of the revision, for scripting.')
    output.add_argument(
        '--format-url',
        action='store_true',
        help='will print just the url of the revision, for scripting.')

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

    d = {
        'id': args.revision_id,
        'diffid': diff_id,
        'fields': fields,
        'message': args.message
    }

    result = conduit("differential.updaterevision", d)

    if args.format_id:
        print(result["revisionid"])
    elif args.format_url:
        print(result["uri"])
    else:  # args.format_summary:
        print((
            "Updated revision '{rev_id}', you can view it at this URL:\n"
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
