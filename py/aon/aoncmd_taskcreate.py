"""Create a new task in maniphest.

you can use the 'task id' output from this command as input to the
'arcyon task-update' command.

usage examples:
    create a new task with just a title:
    $ arcyon task-create 'title'
    99

    create a new task with a title and description:
    $ arcyon task-create 'title' -d 'a description of the task'
    99

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_taskcreate
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
from __future__ import print_function

import sys
import textwrap

import phlcon_maniphest
import phlsys_makeconduit

import aont_conduitargs


def getFromfilePrefixChars():
    return ""


def setupParser(parser):

    # make a list of priority names in increasing order of importance
    priority_name_list = phlcon_maniphest.PRIORITIES.keys()
    priority_name_list.sort(
        key=lambda x: phlcon_maniphest.PRIORITIES[x])

    priorities = parser.add_argument_group(
        'priority arguments',
        'use any of ' + textwrap.fill(
            str(priority_name_list)))

    parser.add_argument(
        'title',
        metavar='STRING',
        help='the short title of the task',
        type=str)

    parser.add_argument(
        '--description',
        '-d',
        metavar='STRING',
        help='the long description of the task',
        type=str)

    priorities.add_argument(
        '--priority', '-p',
        choices=priority_name_list,
        metavar="PRIORITY",
        default=None,
        type=str,
        help="perform an action on a review")

    aont_conduitargs.addArguments(parser)


def process(args):
    if not args.title.strip():
        print('you must supply a non-empty title', file=sys.stderr)
        return 1

    # create_task expects an integer
    priority = None
    if args.priority is not None:
        priority = phlcon_maniphest.PRIORITIES[args.priority]

    conduit = phlsys_makeconduit.make_conduit(args.uri, args.user, args.cert)
    result = phlcon_maniphest.create_task(
        conduit, args.title, args.description, priority)

    print(result.uri)


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
