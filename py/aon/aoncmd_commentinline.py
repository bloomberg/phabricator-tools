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
# ------------------------------ END-OF-FILE ----------------------------------
