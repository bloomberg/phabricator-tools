"""create a comment on differential reviews.

usage examples:
    comment on revision '1':
    $ arcyon comment 1 -m 'hello revision 1, how are you?'

    accept revision '1':
    $ arcyon comment 1 -m 'looks good' --action accept

    comment on revisions 1 and 2, reading the message from 'mymessage':
    $ arcyon comment 1 2 --message-file mymessage

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_comment
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

import argparse
import sys
import textwrap

import phlcon_differential
import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    actions = parser.add_argument_group(
        'action arguments',
        'use any of ' + textwrap.fill(
            str(phlcon_differential.USER_ACTIONS.keys())))

    parser.add_argument(
        'ids',
        type=int,
        nargs="*",
        default=[],
        help="the revisions to comment on (e.g. 1)")
    parser.add_argument(
        '--ids-file',
        metavar='FILE',
        type=argparse.FileType('r'),
        help="a file to read ids from, use '-' to specify stdin")

    parser.add_argument(
        '--message', '-m',
        metavar="M",
        default="",
        type=str,
        help="the body text of the comment")
    parser.add_argument(
        '--message-file',
        metavar='FILE',
        type=argparse.FileType('r'),
        help="a file to read the message from, use '-' for stdin")
    parser.add_argument(
        '--silent',
        action='store_true',
        help="don't send notification emails for this comment")
    parser.add_argument(
        '--attach-inlines',
        action='store_true',
        help="attach pending inline comments")
    actions.add_argument(
        '--action', '-a',
        choices=phlcon_differential.USER_ACTIONS.keys(),
        metavar="ACTION",
        default='comment',
        type=str,
        help="perform an action on a review")

    phlsys_makeconduit.add_argparse_arguments(parser)


def process(args):
    conduit = phlsys_makeconduit.make_conduit(
        args.uri, args.user, args.cert, args.act_as_user)

    d = {
        'message': args.message,
        'silent': args.silent,
        'action': phlcon_differential.USER_ACTIONS[args.action],
        'attach_inlines': args.attach_inlines
    }

    if args.message_file:
        d['message'] += args.message_file.read()

    ids = args.ids
    if args.ids_file:
        ids.extend([int(i) for i in args.ids_file.read().split()])

    if not ids:
        print "error: you have not specified any revision ids"
        sys.exit(1)

    for i in ids:
        d["revision_id"] = i
        conduit("differential.createcomment", d)


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
