"""git-phab-log  - a Phabricator git-log parser.

Examine your git log for commits from Phabricator and associated info.

Operates on a list of Git commit hashes, which can be supplied by you on stdin
or calculated from commits that you provide as parameters.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# gabcmd_gitphablog
#
# Public Functions:
#   parse_args
#   main
#   passes_filters
#   get_revision_generator
#   parse_fields
#   parse_valid_fields
#
# Public Assignments:
#   FIELDS_LISTS
#   FIELDS_SINGLE_VALUE
#   FIELDS_TEXT
#   ALL_VALID_FIELDS
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import argparse
import collections
import re
import signal

import phlgit_log
import phlgit_revlist
import phlsys_git


_USAGE_EXAMPLES = """
usage examples:
    list information about revisions on your current branch:
    $ git-phab-log

    list information about commits on your branch but not 'origin/master':
    $ git-phab-log origin/master..

    list unreviewed commits on your branch:
    $ git-phab-log origin/master..

    list information about non-merge revisions on your current branch:
    $ git rev-list HEAD --no-merges | git-phab-log list-file -
"""

# these fields were compiled from observation of logs alone
# TODO: get the from the Phabricator source

FIELDS_LISTS = [
    'maniphest tasks',
    'reviewed by',
    'reviewers',
    'auditors',
    'cc',
]

FIELDS_SINGLE_VALUE = [
    'differential revision',
]

FIELDS_TEXT = [
    'test plan',
    'summary',
    'conflicts',
]

ALL_VALID_FIELDS = FIELDS_LISTS + FIELDS_SINGLE_VALUE + FIELDS_TEXT


def _get_set_or_none(list_or_none):
    if list_or_none is not None:
        list_or_none = set(list_or_none)
    return list_or_none


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    parser.add_argument(
        'commits',
        metavar="COMMITS",
        type=str,
        nargs='*',
        help="commits to traverse the 'parent' links of, to make the list of "
             "revisions to display. e.g. 'origin/master', 'origin/master..'. "
             "defaults to 'HEAD' if none are supplied here or via --list-file")

    parser.add_argument(
        '--list-file',
        metavar='FILE',
        type=argparse.FileType('r'),
        help="optional file to read list of commit from, use '-' to read from "
             "stdin")

    parser.add_argument(
        '--only-phab-reviewed',
        action='store_true',
        help="show only Phabricator-reviewed revisions")

    parser.add_argument(
        '--no-phab-reviewed',
        action='store_true',
        help="show only revisions that were not Phabricator-reviewed")

    parser.add_argument(
        '--approved-by-any-of',
        metavar='USERNAME',
        type=str,
        nargs='+',
        help="show only Phabricator-reviewed revisions approved by these.")

    parser.add_argument(
        '--approved-by-none-of',
        metavar='USERNAME',
        type=str,
        nargs='+',
        help="show only revisions not approved by these.")

    args = parser.parse_args()

    # these lists need to be sets for correctness and performance
    args.approved_by_any_of = _get_set_or_none(args.approved_by_any_of)
    args.approved_by_none_of = _get_set_or_none(args.approved_by_none_of)

    return args


def main():
    # ignore SIGPIPE or we'll be incompatible with commands like 'head'
    #
    # see:
    # http://newbebweb.blogspot.co.uk/2012/02/python-head-ioerror-errno-32-
    #                                                               broken.html
    #
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    args = parse_args()

    for revision in get_revision_generator(args):
        fields = parse_fields(revision.message)

        if not passes_filters(args, fields):
            continue

        # all bets are off if there's no differential revision
        review_url = fields.get('differential revision', None)
        if review_url is None:
            fields = {}
            review_url = ""

        reviewed_by = fields.get('reviewed by', None)
        if reviewed_by is not None:
            reviewed_by = ','.join(reviewed_by)
        else:
            reviewed_by = ""

        print "{commit_hash} {review_url} {reviewer}".format(
            commit_hash=revision.abbrev_hash,
            review_url=review_url,
            reviewer=reviewed_by)


def passes_filters(args, fields):
    is_phab_reviewed = 'differential revision' in fields

    # approved_by should be a set of approvers or None
    approved_by = fields.get('reviewed by', None)
    if is_phab_reviewed:
        if approved_by is not None:
            approved_by = set(approved_by)
    else:
        approved_by = None

    if args.only_phab_reviewed and not is_phab_reviewed:
        return False

    if args.no_phab_reviewed and is_phab_reviewed:
        return False

    required_approvers = args.approved_by_any_of
    if required_approvers:
        if not approved_by or not approved_by.issubset(required_approvers):
            return False

    banned_approvers = args.approved_by_none_of
    if banned_approvers:
        if approved_by and not approved_by.isdisjoint(banned_approvers):
            return False

    return True


def get_revision_generator(args):

    clone = phlsys_git.GitClone('.')

    commit_list = []
    commits_to_follow = []
    did_specify_something = False

    if args.commits:
        did_specify_something = True
        commits_to_follow = args.commits

    if args.list_file:
        did_specify_something = True
        commit_list += args.list_file.read()

    if not did_specify_something:
        commits_to_follow = ['HEAD']

    if commits_to_follow:
        commit_list += phlgit_revlist.commits(clone, *commits_to_follow)

    make_rev = phlgit_log.make_revision_from_hash
    revision_generator = (make_rev(clone, commit) for commit in commit_list)

    return revision_generator


def parse_fields(message_body):
    fields = parse_valid_fields(message_body)

    # turn the list fields into space-separated lists
    for field in fields:
        if field in FIELDS_LISTS:
            list_items = fields[field].split()
            list_items = [l.strip(',') for l in list_items]
            fields[field] = list_items
        elif field in FIELDS_SINGLE_VALUE:
            fields[field] = fields[field].strip()

    return fields


def parse_valid_fields(message_body):
    identifier_re = re.compile('(\w+( \w+)*):\s*')
    current_field = 'summary'
    fields = collections.defaultdict(str)
    for line in message_body.splitlines():
        match = identifier_re.match(line)
        if match:
            lower_match = match.group(1).lower()
            if match and lower_match in ALL_VALID_FIELDS:
                current_field = lower_match
                line = line[len(match.group(0)):]
        if current_field:
            fields[current_field] += line + '\n'
    return dict(fields)


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
