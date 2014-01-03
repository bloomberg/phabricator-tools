"""display and filter the list of maniphest tasks.

you can use the 'task id' output from this command as input to the
'arcyon task-update' command.

usage examples:
    list all tasks:
    $ arcyon task-query

output formats:
    --format-ids
        3
        2
        1

    --format-short
        8 / Open / High / rethink the blob module
        7 / Open / High / document the lifecycle of a request
        3 / Open / Low / extract methods out of the doWork() function

    --format-python
        [{'description': u'',
          'id': u'1',
          'objectName': u'T1',
          'priority': u'Needs Triage',
          'status': u'0',
          ...

    --format-json
        [
          {
            "description": "",
            "id": "1",
            "objectName": "T1",
        ...

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_taskquery
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

import json
import pprint
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
        'Mutually exclusive, defaults to "--format-short"')
    output = output_group.add_mutually_exclusive_group()
    opt = parser.add_argument_group(
        'Optional task arguments')

    priorities.add_argument(
        '--priorities',
        '-p',
        nargs="*",
        choices=priority_name_list,
        metavar="PRIORITY",
        default=None,
        type=str,
        help="filter by priority of the task")
    opt.add_argument(
        '--order',
        choices=phlcon_maniphest.ORDERS.keys(),
        default=None,
        type=str,
        help="the ordering of the returned results")
    opt.add_argument(
        '--ids',
        nargs="+",
        metavar='INT',
        default=[],
        help='specific task ids to restrict the query to',
        type=str)
    opt.add_argument(
        '--owners',
        '-o',
        nargs="+",
        metavar='USER',
        default=[],
        help='specific owners usernames to restrict the query to',
        type=str)
    opt.add_argument(
        '--authors',
        nargs="+",
        metavar='USER',
        default=[],
        help='specific author usernames to restrict the query to',
        type=str)
    opt.add_argument(
        '--ccs',
        '-c',
        nargs="+",
        metavar='USER',
        default=[],
        help='specific cc usernames to restrict the query to',
        type=str)
    opt.add_argument(
        '--projects',
        nargs="+",
        metavar='PROJECT',
        default=[],
        help='a list of project names to restrict the query',
        type=str)
    opt.add_argument(
        '--status',
        type=str,
        default=None,
        choices=phlcon_maniphest.STATUS_FILTERS.keys(),
        help='a single status type to restrict items to')
    opt.add_argument(
        '--text',
        type=str,
        metavar='STRING',
        default=None,
        help='string to search the full text of each task for.')
    opt.add_argument(
        '--max-results',
        type=int,
        metavar='INT',
        default=None,
        help='limit the number of results returned, if unspecified then the '
             'server default limit is used (seems to be 1000).')
    opt.add_argument(
        '--offset-results',
        type=int,
        metavar='INT',
        default=None,
        help='where there is a limit on the number of results, you can supply '
             'an offset to return the next batch of results. e.g. if the '
             'number of results is limited to 100, then to see the next "page"'
             'of results, supply an offset of 100.  To see "page 3" of the '
             'results, supply an offset of 200 and so on.  Theres no way to '
             'count the total number of results at present.')

    output.add_argument(
        '--format-short',
        action='store_true',
        help='will print a short human-readable summary of each task.')
    output.add_argument(
        '--format-ids',
        action='store_true',
        help='will print just the ids of the tasks, for scripting.')
    output.add_argument(
        '--format-string',
        type=str,
        default=None,
        help='will print using the supplied format string, e.g. "{id}" '
             'to print a list of ids.  use --format-python to list all the '
             'available attributes for printing.')
    output.add_argument(
        '--format-python',
        action='store_true',
        help='will pretty-print the response as a python object.')
    output.add_argument(
        '--format-json',
        action='store_true',
        help='will pretty-print the response in json.')

    phlsys_makeconduit.add_argparse_arguments(parser)


def _combine_lists_if_not_none(*lists):
    result = []

    for l in lists:
        if l is not None:
            result += l

    return result


def process(args):
    conduit = phlsys_makeconduit.make_conduit(args.uri, args.user, args.cert)

    # conduit expects PHIDs not plain usernames
    user_phids = phlcon_user.UserPhidCache(conduit)
    user_phids.add_hint_list(
        _combine_lists_if_not_none(args.owners, args.ccs))
    authors = [user_phids.get_phid(user) for user in args.authors]
    owners = [user_phids.get_phid(user) for user in args.owners]
    ccs = [user_phids.get_phid(user) for user in args.ccs]

    # conduit expects PHIDs not plain project names
    projects = None
    if args.projects:
        project_to_phid = phlcon_project.make_project_to_phid_dict(conduit)
        projects = [project_to_phid[p] for p in args.projects]

    filters = phlcon_maniphest.STATUS_FILTERS
    status = filters[args.status] if args.status is not None else None

    orderings = phlcon_maniphest.ORDERS
    order = orderings[args.order] if args.order is not None else None

    results = phlcon_maniphest.query(
        conduit,
        ids=args.ids,
        authors=authors,
        owners=owners,
        ccs=ccs,
        projects=projects,
        status=status,
        limit=args.max_results,
        offset=args.offset_results,
        order=order,
        text=args.text)

    results = [dict(r.__dict__) for r in results]

    for r in results:
        r['statusName'] = phlcon_maniphest.STATUSES[int(r['status'])]

    # initialise to format for 'args.format_short'
    output_format = "{id} / {statusName} / {priority} / {title}"

    if args.format_ids:
        output_format = "{id}"
    elif args.format_string is not None:
        output_format = args.format_string

    if args.format_python:
        pprint.pprint(results)
    elif args.format_json:
        print(json.dumps(results, sort_keys=True, indent=2))
    else:
        for r in results:
            print(output_format.format(**r))


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
