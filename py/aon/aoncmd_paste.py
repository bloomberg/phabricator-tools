"""Create a new paste.

Usage examples:
    Create a paste from an argument:
    $ arcyon paste "paste title" -t "This is a paste."
    https://your.phabricator.test/P1

    Create a paste from stdin:
    $ cat a_file | arcyon paste "paste title" -f -
    https://your.phabricator.test/P2

    Create a paste from file:
    $ arcyon paste "paste title" -f path/to/file
    https://your.phabricator.test/P3

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_paste
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
import argparse
import sys

import aont_conduitargs
import phlcon_paste
import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    parser.add_argument(
        'title',
        type=str,
        help="Title of the paste.")

    text_arg_group = parser.add_mutually_exclusive_group(required=True)

    text_arg_group.add_argument(
        '--text', "-t",
        type=str,
        default="",
        help="Text of the paste.")
    text_arg_group.add_argument(
        '--text-file', "-f",
        metavar='FILENAME',
        type=argparse.FileType('r'),
        help="a file to read the paste from, use '-' to specify stdin")

    parser.add_argument(
        '--language', '-l',
        metavar="LANGUAGE",
        type=str,
        default=None,
        help="The language of the paste ie. C++, java etc. default detects"
        "from filename in title."
    )

    parser.add_argument(
        '--format-id', '--id',
        action="store_true",
        dest="format_id",
        help="only print the ID of the paste")
    parser.add_argument(
        '--act-as-user',
        type=str,
        metavar="USERNAME",
        help="impersonate a user (admin only)")

    aont_conduitargs.addArguments(parser)


def process(args):
    conduit = phlsys_makeconduit.make_conduit(args.uri, args.user, args.cert)

    if args.act_as_user:
        conduit.set_act_as_user(args.act_as_user)

    if args.text:
        text = args.text
    elif args.text_file:
        text = args.text_file.read()
    else:
        print "error: you have not specified any content for the paste"
        sys.exit(1)

    result = phlcon_paste.create_paste(
        conduit, text, args.title, args.language)
    print result.uri if not args.format_id else result.id


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
