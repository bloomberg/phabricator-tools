"""Get a diff from differential, along with metadata.

usage examples:
    list the files affected by revision 1
    $ arcyon get-diff -r 1 --ls
    /file1
    /dir/file2

    list the branch and files
    $ arcyon get-diff -r 1 --fs "{branch}" "{oldPath} -> {currentPath}"

output formats:
    --format-python
        {u'bookmark': None,
        u'branch': None,
        u'changes': [{u'addLines': u'0',
                    u'awayPaths': [],
                    u'commitHash': None,
                    u'currentPath': u'NEWFILE',
                    u'delLines': u'0',
                    ...

    --format-json
        {
        "bookmark": null,
        "branch": null,
        "changes": [
            {
            "addLines": "0",
            "awayPaths": [],
            "commitHash": null,
            "currentPath": "NEWFILE",
            "delLines": "0",
            ...

    --format-unified
        diff -uNard a/ b/
        +++ a/foo.c
        --- b/foo.c
        @@ 1,3 +0,0 @@
         some
        +content
        -contnet
         file
        ...

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_getdiff
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#   unified_diff
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import json
import pprint

import phlcon_differential
import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    diffsrc_group = parser.add_argument_group(
        'Diff arguments',
        'Mutually exclusive, one is required')
    diffsrc = diffsrc_group.add_mutually_exclusive_group(required=True)
    output_group = parser.add_argument_group(
        'Output format arguments',
        'Mutually exclusive, defaults to "--list-files"')
    output = output_group.add_mutually_exclusive_group()

    diffsrc.add_argument(
        '--revision',
        '-r',
        metavar='INT',
        help='the id of the revision to get the diff from.',
        type=int)
    diffsrc.add_argument(
        '--diff',
        '-d',
        metavar='INT',
        help='the id of the diff to retrieve.',
        type=int)

    output.add_argument(
        '--list-files',
        '--ls',
        action='store_true',
        help='list only the affected paths, shortcut for the --format-type. '
             'this lists the set of files found in the "currentPath" and '
             '"oldPath" fields of the "changes" field.')
    output.add_argument(
        '--format-python',
        action='store_true',
        help='print python representation of the raw response from '
             'the server.')
    output.add_argument(
        '--format-json',
        action='store_true',
        help='print json representation of the raw response from '
             'the server.')
    output.add_argument(
        '--format-unified',
        action='store_true',
        help='outputs a unified diff that can be used to apply the changes'
             'locally to the working copy')
    output.add_argument(
        '--format-files',
        type=str,
        help='write the files to the specified directory (under left, right)')
    output.add_argument(
        '--format-strings',
        '--fs',
        type=str,
        metavar='STR',
        nargs=2,
        help='specify two custom format strings for displaying the items, '
             'the first string is applied to the whole output, the second '
             'is applied per item in the "changes" dictionary. i.e. '
             '("FORMAT-DIFF", "FORMAT-FOREACH-CHANGE").  the strings will be '
             'applied using Python\'s str.format(), so you can use '
             'curly brackets to substitute for field names, e.g. "\{id\}". '
             'you can use "--format-python" to discover the field names.')

    phlsys_makeconduit.add_argparse_arguments(parser)


def process(args):
    conduit = phlsys_makeconduit.make_conduit(
        args.uri, args.user, args.cert, args.act_as_user)

    if args.revision:
        result = phlcon_differential.get_revision_diff(conduit, args.revision)
    else:
        assert args.diff
        result = phlcon_differential.get_diff(conduit, args.diff)

    if args.format_python:
        pprint.pprint(result)
    elif args.format_json:
        print json.dumps(result, sort_keys=True, indent=2)
    elif args.format_unified:
        print unified_diff(result)
    elif args.format_files:
        phlcon_differential.write_diff_files(result, args.format_files)
    elif args.format_strings:
        fmt = args.format_strings[0]
        fmt_change = args.format_strings[1]
        if fmt:
            print fmt.format(**result)
        if fmt_change:
            for change in result["changes"]:
                print fmt_change.format(**change)
    else:  # args.list_files:
        paths = set()
        for change in result.changes:
            paths.add(change["currentPath"])
            paths.add(change["oldPath"])
        for path in paths:
            print path


def unified_diff(result):
    for change in result.changes:
        print '--- ' + change["oldPath"]
        print '+++ ' + change["currentPath"]
        for hunk in change["hunks"]:
            hunk_format = "@@ -{oldOffset},{oldLength}"
            hunk_format += " +{newOffset},{newLength} @@"
            print hunk_format.format(**hunk)
            print hunk["corpus"]


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
