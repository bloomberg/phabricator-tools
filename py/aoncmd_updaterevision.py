"""Update an existing revision in differential.

usage examples:
    update revision 1 from diff 2:
    $ arcyon update-revision -i 1 -d 2 -m 'fix review issues'
"""

import argparse

import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    diffsrc = parser.add_mutually_exclusive_group(required=True)

    diffsrc.add_argument(
        '--diff-id',
        metavar='INT',
        type=int)
    diffsrc.add_argument(
        '-f', '--raw-diff-file',
        metavar='FILE',
        type=argparse.FileType('r'))

    parser.add_argument(
        '-i', '--revision-id',
        metavar='INT',
        required=True,
        type=str)

    parser.add_argument(
        '-m', '--message',
        metavar='TEXT',
        required=True,
        type=str)


def process(args):
    conduit = phlsys_makeconduit.makeConduit()

    # create a new diff if we need to
    if args.diff_id:
        diff_id = args.diff_id
    else:
        d = {'diff': args.raw_diff_file.read()}
        diff_id = conduit.call("differential.createrawdiff", d)["id"]

    fields = {}

    d = {
        'id': args.revision_id,
        'diffid': diff_id,
        'fields': fields,
        'message': args.message
    }

    result = conduit.call("differential.updaterevision", d)
    print result["revisionid"]


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
