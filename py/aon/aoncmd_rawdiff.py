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

import argparse
import sys

import phlsys_makeconduit

import aont_conduitargs


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
    aont_conduitargs.addArguments(parser)


def process(args):
    conduit = phlsys_makeconduit.makeConduit(args.uri, args.user, args.cert)

    d = {'diff': args.infile.read()}

    result = conduit.call("differential.createrawdiff", d)
    print result["id"]


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
