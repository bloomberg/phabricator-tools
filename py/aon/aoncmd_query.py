"""display and filter the list of differential revisions.

usage examples:
    list all revisions:
    $ arcyon query

    list ids of all revisions:
    $ arcyon query --format-type ids

    list all your open revisions:
    $ arcyon query --author-me --status-type open

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
          ...

    --format-type json
        [
          {
            "authorPHID": "PHID-USER-agn7y2uw2pj4nc5nknhe",
            "branch": null,
            "ccs": [
            "PHID-USER-n334wwtakshsxeau3qij"
            ],
            "commits": [],
            ...

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_query
#
# Public Classes:
#   ValidationError
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

import datetime
import json
import pprint
import string
import sys
import textwrap

import phlcon_user
import phlsys_conduit
import phlsys_dictutil
import phlsys_makeconduit
import phlsys_strtotime
import phlsys_timedeltatostr


def getFromfilePrefixChars():
    return ""


def setupParser(parser):
    filters = parser.add_argument_group('filter parameters')
    self_filters = parser.add_argument_group('self filter parameters')
    user_filters = parser.add_argument_group('user filter parameters')
    time_filters = parser.add_argument_group(
        'time filter parameters',
        textwrap.fill(
            phlsys_strtotime.describe_duration_string_to_time_delta()))
    fmts = parser.add_argument_group(
        'output format parameters', 'choose one only, default is "short"')
    formats = fmts.add_mutually_exclusive_group()

    _setupParserTopLevel(parser)
    _setupParserFilters(filters, self_filters, user_filters, time_filters)

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

    phlsys_makeconduit.add_argparse_arguments(parser)


def _setupParserTopLevel(parser):
    parser.add_argument(
        '--ids',
        type=int,
        metavar='INT',
        nargs='+',
        default=[],
        help='optional list of ids to limit the search to, if none are '
             'supplied then all ids are subject to the query.')
    parser.add_argument(
        '--ids-stdin',
        action='store_true',
        help='read additional list of ids to limit the query to from stdin.')
    parser.add_argument(
        '--translate',
        action='store_true',
        help='translate user PHIDs to usernames and add as new '
             'elements to the output dictionary so theyre visible in python '
             'and json output formats.')
    parser.add_argument(
        '--max-results',
        type=int,
        metavar='INT',
        help='limit the number of results returned, if unspecified then the '
             'server default limit is used (seems to be 1000).')
    parser.add_argument(
        '--offset-results',
        type=int,
        metavar='INT',
        help='where there is a limit on the number of results, you can supply '
             'an offset to return the next batch of results. e.g. if the '
             'number of results is limited to 100, then to see the next "page"'
             'of results, supply an offset of 100.  To see "page 3" of the '
             'results, supply an offset of 200 and so on.  Theres no way to '
             'count the total number of results at present.')
    parser.add_argument(
        '--order',
        choices=['modified', 'created'],
        default='modified',
        help="specify the order for the server to return revisions to us. "
             "In both cases it's 'most recent first'.")


def _setupParserFilters(filters, self_filters, user_filters, time_filters):
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
    filters.add_argument(
        '--arcanist-projects',
        type=str,
        nargs="+",
        default=[],
        metavar='STR',
        help="add projects to the arcanistProjects filter")
    filters.add_argument(
        '--branches',
        type=str,
        nargs="+",
        default=[],
        metavar='STR',
        help="add branches to the branches filter")

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
        '--mine',
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
        type=phlsys_strtotime.duration_string_to_time_delta,
        metavar='AGE',
        help='include reviews which are at least AGE old.')
    time_filters.add_argument(
        '--update-max-age',
        type=phlsys_strtotime.duration_string_to_time_delta,
        metavar='AGE',
        help='include reviews which are at most AGE old.')


def _set_human_times_since(r, kind, since):
    r[u"humanTimeSinceDate" + kind] = phlsys_timedeltatostr.quantized(since)
    r[u"daysSinceDate" + kind] = phlsys_timedeltatostr.in_days(since)
    r[u"weeksSinceDate" + kind] = phlsys_timedeltatostr.in_weeks(since)
    r[u"monthsSinceDate" + kind] = phlsys_timedeltatostr.in_months(since)


class ValidationError(Exception):
    pass


def _validate_args(args):
    if args.act_as_user and any(
        [args.author_me, args.reviewer_me, args.cc_me, args.subscriber_me,
         args.responsible_me]):
        raise ValidationError(
            "self filter parameters (*-me/mine) not allowed in conjunction " +
            "with --act-as-user due to ambiguity")


def _process_user_fields(me, conduit, args):
    d = {}

    def process_user_field(name, param, add_me):
        d[name] = param
        if add_me:
            d[name].append(me)

    process_user_field("authors", args.authors, args.author_me)
    process_user_field("reviewers", args.reviewers, args.reviewer_me)
    process_user_field("ccs", args.ccs, args.cc_me)
    process_user_field("subscribers", args.subscribers, args.subscriber_me)
    process_user_field(
        "responsibleUsers",
        args.responsible_users,
        args.responsible_me)

    # conduit expects PHIDs not plain usernames
    user_phids = phlcon_user.UserPhidCache(conduit)
    for users in d.itervalues():
        user_phids.add_hint_list(users)

    for key in d.iterkeys():
        d[key] = [user_phids.get_phid(u) for u in d[key]]

    return d


def _set_options(args, d):
    phlsys_dictutil.set_if_true(d, 'ids', args.ids)
    phlsys_dictutil.set_if_true(d, 'arcanistProjects', args.arcanist_projects)
    phlsys_dictutil.set_if_true(d, 'branches', args.branches)
    phlsys_dictutil.set_if_true(d, 'limit', args.max_results)
    phlsys_dictutil.set_if_true(d, 'offset', args.offset_results)

    if args.ids_stdin:
        ids = [int(i) for i in " ".join(sys.stdin.readlines()).split()]
        d["ids"] = args.ids + ids

    if args.status_type:
        d["status"] = "status-" + args.status_type


def process(args):
    _validate_args(args)

    uri, user, cert, _ = phlsys_makeconduit.get_uri_user_cert_explanation(
        args.uri, args.user, args.cert)
    conduit = phlsys_conduit.Conduit(uri, user, cert, args.act_as_user)

    d = _process_user_fields(user, conduit, args)
    _set_options(args, d)

    d["order"] = 'order-' + args.order

    # perform the query
    results = conduit("differential.query", d)

    if args.statuses:
        results = [r for r in results if r["statusName"] in args.statuses]

    if args.update_min_age or args.update_max_age:
        results = _exclude_on_update_age(args, results)

    if args.translate:
        # gather user PHIDs
        _translate_user_phids(conduit, results)

    _set_human_times(results)

    _output_results(args, results)


def _translate_user_phids(conduit, results):
    # gather user PHIDs
    user_phids = set()
    for r in results:
        user_phids.add(r["authorPHID"])
        for u in r["ccs"]:
            user_phids.add(u)
        for u in r["reviewers"]:
            user_phids.add(u)

    # get the names back
    phidToUser = {}
    user_phids = list(user_phids)
    if user_phids:
        phidToUser = phlcon_user.make_phid_username_dict(
            conduit, user_phids)

    # do the translation
    for r in results:
        r[u"authorUsername"] = phidToUser[r["authorPHID"]]
        r[u"ccUsernames"] = [phidToUser[u] for u in r["ccs"]]
        r[u"reviewerUsernames"] = [phidToUser[u] for u in r["reviewers"]]


def _exclude_on_update_age(args, results):
    now = datetime.datetime.now()

    def get_age(r):
        return now - datetime.datetime.fromtimestamp(float(r["dateModified"]))

    if args.update_min_age:
        results = [r for r in results if get_age(r) >= args.update_min_age]

    if args.update_max_age:
        results = [r for r in results if get_age(r) <= args.update_max_age]

    return results


def _set_human_times(results):
    now = datetime.datetime.now()
    for r in results:
        date_created = datetime.datetime.fromtimestamp(float(r["dateCreated"]))
        date_modified = datetime.datetime.fromtimestamp(
            float(r["dateModified"]))

        since_modified = now - date_modified
        since_created = now - date_created

        _set_human_times_since(r, 'Modified', since_modified)
        _set_human_times_since(r, 'Created', since_created)

        r[u"humanDateModified"] = str(date_modified)
        r[u"humanDateCreated"] = str(date_created)


def _output_results(args, results):
    if not args.format_type and not args.format_string:
        args.format_type = "short"
    if args.format_type:
        if args.format_type == "json":
            print(json.dumps(
                results, sort_keys=True, indent=2).encode('utf-8'))
        elif args.format_type == "python":
            pprint.pprint(results)
        elif args.format_type == "short":
            shortTemplate = string.Template("$id / $statusName / $title")
            for x in results:
                print(shortTemplate.safe_substitute(x).encode('utf-8'))
        elif args.format_type == "ids":
            shortTemplate = string.Template("$id")
            for x in results:
                print(shortTemplate.safe_substitute(x).encode('utf-8'))
        else:
            raise Exception("unsupported format")
    else:  # args.format_string
        assert args.format_string
        template = string.Template(args.format_string)
        for x in results:
            print(template.safe_substitute(x).encode('utf-8'))


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2016 Bloomberg Finance L.P.
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
