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
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys

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

    phlsys_makeconduit.add_argparse_arguments(parser)


def process(args):
    conduit = phlsys_makeconduit.make_conduit(
        args.uri, args.user, args.cert, args.act_as_user)

    if args.text:
        text = args.text
    elif args.text_file:
        text = args.text_file.read()
    else:
        print("error: you have not specified any content for the paste")
        sys.exit(1)

    result = phlcon_paste.create_paste(
        conduit, text, args.title, args.language)
    print(result.uri if not args.format_id else result.id)


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
