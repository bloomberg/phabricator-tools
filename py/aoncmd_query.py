"""display and filter the list of differential revisions.

usage examples:
    list all revisions:
    $ arcyon query

    list ids of all revisions:
    $ arcyon query --format-type ids

    list all your open revisions:
    $ arcyon query --author-mine --status-type open

    list all open revisions updated over a week ago
    $ arcyon query --status-type open --update-min-age "1 weeks"

output formats:
    --format-type ids
        3
        2
        1

    --format-type short
        8 / Accepted / add NEWFILE
        7 / Accepted / add NEWFILE
        3 / Accepted / add NEWFILE

    --format-type python
        [{u'authorPHID': u'PHID-USER-agn7y2uw2pj4nc5nknhe',
          u'branch': None,
          u'ccs': [u'PHID-USER-n334wwtakshsxeau3qij'],
          u'commits': [],
          u'dateCreated': u'1362827032',
          u'dateModified': u'1362827033',
          u'diffs': [u'5', u'4'],
          u'hashes': [],
          u'id': u'3',
          u'lineCount': u'0',
          u'phid': u'PHID-DREV-4vkkcnkcoyxmf4us4t2l',
          u'reviewers': [u'PHID-USER-hncf4pdbrr53lsxn5j6z'],
          u'status': u'2',
          u'statusName': u'Accepted',
          u'summary': u'',
          u'testPlan': u'test plan',
          u'title': u'add NEWFILE',
          u'uri': u'http://127.0.0.1/D3'}]

    --format-type json
        [
          {
            "authorPHID": "PHID-USER-agn7y2uw2pj4nc5nknhe",
            "branch": null,
            "ccs": [
            "PHID-USER-n334wwtakshsxeau3qij"
            ],
            "commits": [],
            "dateCreated": "1362827032",
            "dateModified": "1362827033",
            "diffs": [
            "5",
            "4"
            ],
            "hashes": [],
            "id": "3",
            "lineCount": "0",
            "phid": "PHID-DREV-4vkkcnkcoyxmf4us4t2l",
            "reviewers": [
            "PHID-USER-hncf4pdbrr53lsxn5j6z"
            ],
            "status": "2",
            "statusName": "Accepted",
            "summary": "",
            "testPlan": "test plan",
            "title": "add NEWFILE",
            "uri": "http://127.0.0.1/D3"
          }
        ]
"""

import datetime
import json
import pprint
import string
import textwrap

import phlcon_user
import phlsys_strtotime
import phlsys_makeconduit


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    filters = parser.add_argument_group('filter parameters')
    self_filters = parser.add_argument_group('self filter parameters')
    user_filters = parser.add_argument_group('user filter parameters')
    time_filters = parser.add_argument_group(
        'time filter parameters',
        textwrap.fill(
            phlsys_strtotime.describeDurationStringToTimeDelta()))
    fmts = parser.add_argument_group(
        'output format parameters', 'choose one only, default is "short"')
    formats = fmts.add_mutually_exclusive_group()

    filters.add_argument(
        '--status-type',
        type=str,
        choices=['open', 'accepted', 'closed'],
        help="limit output to only this status type")
    filters.add_argument(
        '--statuses',
        type=str,
        nargs="+",
        choices=[
            'Closed',
            'Abandoned',
            'Needs Review',
            'Needs Revision',
            'Accepted'],
        help="limit output to only these statuses")

    self_filters.add_argument(
        '--author-me',
        action='store_true',
        help="add yourself to the authors filter")
    self_filters.add_argument(
        '--reviewer-me',
        action='store_true',
        help="add yourself to the reviewers filter")
    self_filters.add_argument(
        '--cc-me',
        action='store_true',
        help="add yourself to the ccs filter")
    self_filters.add_argument(
        '--subscriber-me',
        action='store_true',
        help="add yourself to the subscribers filter")
    self_filters.add_argument(
        '--responsible-me',
        action='store_true',
        help="add yourself to the responsibleUsers filter")

    user_filters.add_argument(
        '--authors',
        type=str,
        nargs="+",
        default=[],
        metavar='USER',
        help="add usernames to the authors filter")
    user_filters.add_argument(
        '--reviewers',
        type=str,
        nargs="+",
        default=[],
        metavar='USER',
        help="add usernames to the reviewers filter")
    user_filters.add_argument(
        '--ccs',
        type=str,
        nargs="+",
        default=[],
        metavar='USER',
        help="add usernames to the ccs filter")
    user_filters.add_argument(
        '--subscribers',
        type=str,
        nargs="+",
        default=[],
        metavar='USER',
        help="add usernames to the subscribers filter")
    user_filters.add_argument(
        '--responsible-users',
        type=str,
        nargs="+",
        default=[],
        metavar='USER',
        help="add usernames to the responsibleUsers filter")

    time_filters.add_argument(
        '--update-min-age',
        type=phlsys_strtotime.durationStringToTimeDelta,
        metavar='AGE',
        help='include reviews which are at least AGE old.')
    time_filters.add_argument(
        '--update-max-age',
        type=phlsys_strtotime.durationStringToTimeDelta,
        metavar='AGE',
        help='include reviews which are at most AGE old.')

    formats.add_argument(
        '--format-type',
        choices=['ids', 'short', 'python', 'json'],
        help="see usage examples for sample output")
    formats.add_argument(
        '--format-string',
        metavar='FORMAT',
        type=str,
        help="compose your own output format, e.g. '$id $title', see "
                "usage examples for more details")


def process(args):
    conduit = phlsys_makeconduit.makeConduit()
    me = conduit.getUser()

    d = {}

    def processUserField(name, param, add_me):
        d[name] = param
        if add_me:
            d[name].append(me)

    processUserField("authors", args.authors, args.author_me)
    processUserField("reviewers", args.reviewers, args.reviewer_me)
    processUserField("ccs", args.ccs, args.cc_me)
    processUserField("subscribers", args.subscribers, args.subscriber_me)
    processUserField(
        "responsibleUsers",
        args.responsible_users,
        args.responsible_me)

    users = [u for users in d.itervalues() for u in users]
    users = list(set(users))
    userToPhid = {}
    if users:
        userToPhid = phlcon_user.makeUsernamePhidDict(conduit, users)

    # XXX: check for duplicates in author and reviewer
    # XXX: check for bad userToPhid
    for key in d.iterkeys():
        d[key] = [userToPhid[u] for u in d[key]]

    if args.status_type:
        d["status"] = "status-" + args.status_type

    results = conduit.call("differential.query", d)

    if args.statuses:
        new_results = []
        for r in results:
            if r["statusName"] in args.statuses:
                new_results.append(r)
        results = new_results

    if args.update_min_age:
        now = datetime.datetime.now()
        new_results = []
        for r in results:
            modified = datetime.datetime.fromtimestamp(
                float(r["dateModified"]))
            age = now - modified
            if age >= args.update_min_age:
                new_results.append(r)
        results = new_results

    if args.update_max_age:
        now = datetime.datetime.now()
        new_results = []
        for r in results:
            modified = datetime.datetime.fromtimestamp(
                float(r["dateModified"]))
            age = now - modified
            if age <= args.update_max_age:
                new_results.append(r)
        results = new_results

    if not args.format_type and not args.format_string:
        args.format_type = "short"
    if args.format_type:
        if args.format_type == "json":
            print json.dumps(results, sort_keys=True, indent=2)
        elif args.format_type == "python":
            pprint.pprint(results)
        elif args.format_type == "short":
            shortTemplate = string.Template("$id / $statusName / $title")
            for x in results:
                print shortTemplate.safe_substitute(x)
        elif args.format_type == "ids":
            shortTemplate = string.Template("$id")
            for x in results:
                print shortTemplate.safe_substitute(x)
        else:
            raise Exception("unsupported format")
    else:
        template = string.Template(args.format_string)
        for x in results:
            print template.safe_substitute(x)


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
