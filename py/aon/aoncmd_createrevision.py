"""Create a new revision in differential.

you can use the 'revision id' output from this command as input to the
'arcyon update-revision' command.

usage examples:
    create a new revision by piping in a diff:
    $ diff -u file1 file2 | arcyon create-revision -t title -p plan -f -
    99

    create a new revision from diff 1:
    $ arcyon create-revision -d 1 -t 'title' -p 'test plan'
    99

    create a new revision from diff 1, add a reviewer and a cc:
    $ arcyon create-revision -d 1 -t title -p test -r reviewer -c cc
    99

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_createrevision
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

import phlcon_differential
import phlcon_user
import phlsys_makeconduit

import aont_conduitargs


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    diffsrc_group = parser.add_argument_group(
        'Diff arguments',
        'Mutually exclusive, one is required')
    diffsrc = diffsrc_group.add_mutually_exclusive_group(required=True)
    req = parser.add_argument_group(
        'Required revision arguments',
        'Phabricator requires that you supply both of these')
    opt = parser.add_argument_group(
        'Optional revision arguments',
        'You can supply these later via the web interface if you wish')

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

    req.add_argument(
        '--title',
        '-t',
        metavar='TEXT',
        required=True,
        help='a short description of the changes to review',
        type=str)
    req.add_argument(
        '--test-plan',
        '-p',
        metavar='TEXT',
        required=True,
        help='how you tested your changes and how the reviewer'
             'can verify them',
        type=str)

    opt.add_argument(
        '--summary',
        '-s',
        metavar='TEXT',
        help='a longer summary of the changes to review',
        type=str)
    opt.add_argument(
        '--reviewers',
        '-r',
        nargs="*",
        metavar='USER',
        help='a list of reviewer usernames',
        type=str)
    opt.add_argument(
        '--ccs',
        '-c',
        nargs="*",
        metavar='USER',
        help='a list of usernames to cc on the review',
        type=str)

#   parser.add_argument(
#       '--deps', '--depends-on',
#       nargs="*",
#       metavar='ID',
#       type=int)

    aont_conduitargs.addArguments(parser)


def process(args):
    conduit = phlsys_makeconduit.make_conduit(args.uri, args.user, args.cert)

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
        userToPhid = phlcon_user.make_username_phid_dict(conduit, users)
    for key in fields.iterkeys():
        fields[key] = [userToPhid[u] for u in fields[key]]

    fields[MessageFields.title] = args.title
    fields[MessageFields.test_plan] = args.test_plan
    if args.summary:
        fields[MessageFields.summary] = args.summary

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
