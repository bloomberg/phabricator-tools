"""Create a new revision in differential.

usage examples:
    create a new revision from diff 1:
    $ arcyon create-revision -d 1 -t 'title' -p 'test plan'
"""

import argparse

import phlcon_differential
import phlcon_user
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
        '-t', '--title',
        metavar='TEXT',
        required=True,
        type=str)
    parser.add_argument(
        '-p', '--test-plan',
        metavar='TEXT',
        required=True,
        type=str)
    parser.add_argument(
        '-s', '--summary',
        metavar='TEXT',
        type=str)
    parser.add_argument(
        '-r', '--reviewers',
        nargs="*",
        metavar='TEXT',
        type=str)
    parser.add_argument(
        '-c', '--ccs',
        nargs="*",
        metavar='TEXT',
        type=str)

#   parser.add_argument(
#       '--deps', '--depends-on',
#       nargs="*",
#       metavar='ID',
#       type=int)


def process(args):
    conduit = phlsys_makeconduit.makeConduit()

    # create a new diff if we need to
    if args.diff_id:
        diff_id = args.diff_id
    else:
        d = {'diff': args.raw_diff_file.read()}
        diff_id = conduit.call("differential.createrawdiff", d)["id"]

    fields = {}

    MessageFields = phlcon_differential.MessageFields

    if args.reviewers:
        fields[MessageFields.reviewer_phids] = args.reviewers
    if args.ccs:
        fields[MessageFields.cc_phids] = args.ccs

    # convert all the usernames to userPHIDs
    # TODO: extract function and share with 'query'
    users = [u for users in fields.itervalues() for u in users]
    users = list(set(users))
    userToPhid = {}
    if users:
        userToPhid = phlcon_user.makeUsernamePhidDict(conduit, users)
    for key in fields.iterkeys():
        fields[key] = [userToPhid[u] for u in fields[key]]

    fields[MessageFields.title] = args.title
    fields[MessageFields.test_plan] = args.test_plan
    if args.summary:
        d[MessageFields.summary] = args.summary

    d = {'diffid': diff_id, 'fields': fields}

    result = conduit.call("differential.createrevision", d)
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
