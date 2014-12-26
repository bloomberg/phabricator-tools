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
from __future__ import division
from __future__ import print_function

import sys
import textwrap

import phlcon_maniphest
import phlcon_project
import phlcon_user
import phlsys_makeconduit


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

    phlsys_makeconduit.add_argparse_arguments(parser)


def process(args):
    if args.title and not args.title.strip():
        print('you must supply a non-empty title', file=sys.stderr)
        return 1

    conduit = phlsys_makeconduit.make_conduit(
        args.uri, args.user, args.cert, args.act_as_user)

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
