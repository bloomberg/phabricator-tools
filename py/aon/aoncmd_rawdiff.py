"""Create a raw diff in differential.

you can use the 'diff id' output from this command as input to the
'arcyon create-revision' and 'arcyon update-revision' commands.

usage examples:
    create a new raw diff by piping in a diff:
    $ diff -u file1 file2 | arcyon raw-diff
    99

    create a new raw diff by piping in a file:
    $ arcyon raw-diff < mydiff
    99

    create a new raw diff by loading a file:
    $ arcyon raw-diff mydiff
    99

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_rawdiff
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

import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    parser.add_argument(
        'infile',
        metavar='INFILE',
        nargs='?',
        type=argparse.FileType('r'),
        help="where to read the diff from, can be filename or '-' for stdin. "
             "default is stdin if not specified.",
        default=sys.stdin)
    phlsys_makeconduit.add_argparse_arguments(parser)


def process(args):
    conduit = phlsys_makeconduit.make_conduit(
        args.uri, args.user, args.cert, args.act_as_user)

    d = {'diff': args.infile.read()}

    result = conduit("differential.createrawdiff", d)
    print(result["id"])


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
