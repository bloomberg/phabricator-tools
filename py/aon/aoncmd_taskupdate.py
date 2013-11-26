"""Update a task in maniphest.

you can use the 'task id' output from the 'arcyon task-create' command as input
to this command.

usage examples:
    update task '99' with a new title, only show id:
    $ arcyon task-update 99 -t 'title' --format-id
    99

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_taskupdate
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
import phlcon_project
import phlcon_user
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
        'optional priority arguments',
        'use any of ' + textwrap.fill(
            str(priority_name_list)))
    output_group = parser.add_argument_group(
        'Output format arguments',
        'Mutually exclusive, defaults to "--format-summary"')
    output = output_group.add_mutually_exclusive_group()
    opt = parser.add_argument_group(
        'Optional task arguments',
        'You can supply these later via the web interface if you wish')

    priorities.add_argument(
        '--priority',
        '-p',
        choices=priority_name_list,
        metavar="PRIORITY",
        default=None,
        type=str,
        help="the priority or importance of the task")

    parser.add_argument(
        'id',
        metavar='INT',
        help='the id of the task',
        type=str)

    parser.add_argument(
        '--title',
        '-t',
        metavar='STRING',
        help='the short title of the task',
        default=None,
        type=str)

    opt.add_argument(
        '--description',
        '-d',
        metavar='STRING',
        help='the long description of the task',
        default=None,
        type=str)
    opt.add_argument(
        '--owner',
        '-o',
        metavar='USER',
        help='the username of the owner',
        type=str)
    opt.add_argument(
        '--ccs',
        '-c',
        nargs="*",
        metavar='USER',
        help='a list of usernames to cc on the task',
        type=str)
    opt.add_argument(
        '--projects',
        nargs="*",
        metavar='PROJECT',
        default=[],
        help='a list of project names to add the task to',
        type=str)
    opt.add_argument(
        '--comment',
        '-m',
        metavar='STRING',
        help='an optional comment to make on the task',
        default=None,
        type=str)

    output.add_argument(
        '--format-summary',
        action='store_true',
        help='will print a human-readable summary of the result.')
    output.add_argument(
        '--format-id',
        action='store_true',
        help='will print just the id of the new task, for scripting.')
    output.add_argument(
        '--format-url',
        action='store_true',
        help='will print just the url of the new task, for scripting.')

    aont_conduitargs.addArguments(parser)


def process(args):
    if args.title and not args.title.strip():
        print('you must supply a non-empty title', file=sys.stderr)
        return 1

    conduit = phlsys_makeconduit.make_conduit(args.uri, args.user, args.cert)

    # create_task expects an integer
    priority = None
    if args.priority is not None:
        priority = phlcon_maniphest.PRIORITIES[args.priority]

    # conduit expects PHIDs not plain usernames
    user_phids = phlcon_user.UserPhidCache(conduit)
    if args.owner:
        user_phids.add_hint(args.owner)
    if args.ccs:
        user_phids.add_hint_list(args.ccs)
    owner = user_phids.get_phid(args.owner) if args.owner else None
    ccs = [user_phids.get_phid(u) for u in args.ccs] if args.ccs else None

    # conduit expects PHIDs not plain project names
    projects = None
    if args.projects:
        project_to_phid = phlcon_project.make_project_to_phid_dict(conduit)
        projects = [project_to_phid[p] for p in args.projects]

    result = phlcon_maniphest.update_task(
        conduit,
        args.id,
        args.title,
        args.description,
        priority,
        owner,
        ccs,
        projects,
        args.comment)

    if args.format_id:
        print(result.id)
    elif args.format_url:
        print(result.uri)
    else:  # args.format_summary:
        message = (
            "Updated task '{task_id}', you can view it at this URL:\n"
            "  {url}"
        ).format(
            task_id=result.id,
            url=result.uri)
        print(message)


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
