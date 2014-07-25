"""create an inline comment on a differential review.

    Note: this will create the comments but not submit them.  You must run
    arcyon comment with the --attach-inlines option in order to actually
    submit these.

usage examples:
    comment on revision '1', file requestprocessor.py, starting on line 5,
    spanning 4 lines in total:
    $ arcyon comment-inline 1 -s 5 -l 3 --filepath requestprocessor.py
      -m 'hello revision 1, these four lines will leak memory, please fix'
    $ arcyon comment 1 --attach-inlines

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_commentinline
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

import phlcon_differential
import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    parser.add_argument(
        'id',
        type=int,
        help="the revision id to comment on (e.g. 1)")
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
        '--filepath', '-f',
        metavar="FILE",
        default="",
        required=True,
        type=str,
        help="the filename of the file to comment on")
    parser.add_argument(
        '--start-line', '-s',
        metavar="#",
        required=True,
        type=int,
        help="starting line of the comment")
    parser.add_argument(
        '--end-line-offset', '-l',
        metavar="#",
        default=0,
        type=int,
        help="number of extra lines the comment should span, the default is 0"
             "meaning that the comment spans one line only.")
    parser.add_argument(
        '--left-side', '-o',
        action='store_true',
        help="comment on the left (old) side of the diff")

    phlsys_makeconduit.add_argparse_arguments(parser)


def process(args):
    conduit = phlsys_makeconduit.make_conduit(
        args.uri, args.user, args.cert, args.act_as_user)

    message = args.message
    if args.message_file:
        message += args.message_file.read()

    result = phlcon_differential.create_inline_comment(
        conduit,
        args.id,
        args.filepath,
        args.start_line,
        message,
        not args.left_side,
        args.end_line_offset)

    print result

# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
