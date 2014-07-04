"""List the reviews and corresponding branches in the current repository.

Usage examples:

    Summarise all the tracked review branches:
        $ barc list
        ID     status         tracked name
        10596  ok             r/master/linkUtil
        10594  ok             r/master/notification-spew

    List just the review ids and the trackers:
        $ barc list --format-string "{review_id} {remote_branch}"
        10596 refs/remotes/origin/dev/arcyd/trackers/rbranch/--/-/ok/r/maste...
        10594 refs/remotes/origin/dev/arcyd/trackers/rbranch/--/-/ok/r/maste...

Output format examples:

    --format-summary
        ID     status         tracked name
        10596  ok             r/master/linkUtil
        10594  ok             r/master/notification-spew

    --format-json
        [
          {
            "remote_base": "refs/remotes/origin/master",
            "review_id": "10596",
            ...
          }
          ...
        ]

    --format-python
        [
          {"remote_base": "refs/remotes/origin/master",
           ...
           "review_id": "10596"},
          ...
        ]

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# barcmd_list
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

import json
import pprint

import abdt_classicnaming
import abdt_compositenaming
import abdt_naming
import abdt_rbranchnaming
import phlgit_showref
import phlgitu_ref
import phlsys_git


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    fmts = parser.add_argument_group(
        'Output format parameters',
        'Choose one only, default is "--format-summary"')
    formats = fmts.add_mutually_exclusive_group()

    formats.add_argument(
        '--format-summary',
        action='store_true',
        help="list the review ids, statuses and review names.")

    formats.add_argument(
        '--format-json',
        action='store_true',
        help="print json representation of managed review branches")

    formats.add_argument(
        '--format-python',
        action='store_true',
        help="print python representation of managed review branches")

    formats.add_argument(
        '--format-string',
        type=str,
        metavar='STR',
        help='specify a custom format strings for displaying the items. '
             'the string will be applied using Python\'s str.format(), '
             'so you can use curly brackets to substitute for field names, '
             'e.g. "{review_id}". you can use "--format-python" to discover '
             'the field names.')


def process(args):
    repo = phlsys_git.Repo('.')

    #
    # First, gather all the data
    #

    # XXX: only supports 'origin' remote at present
    remote = 'origin'

    hash_ref_pairs = phlgit_showref.hash_ref_pairs(repo)
    remote_branch_to_hash = _remote_branches_as_short_local(
        hash_ref_pairs, remote)
    # local_branch_to_hash = _short_local_branches(hash_ref_pairs)

    branch_naming = abdt_compositenaming.Naming(
        abdt_classicnaming.Naming(),
        abdt_rbranchnaming.Naming())

    branch_pairs = abdt_naming.get_branch_pairs(
        remote_branch_to_hash.keys(), branch_naming)

    managed_review_branches = _get_managed_review_branches(
        remote_branch_to_hash, branch_pairs)

    #
    # Finally, decide how to display it
    #

    if args.format_json:
        print json.dumps(managed_review_branches, sort_keys=True, indent=2)
    elif args.format_python:
        pprint.pprint(managed_review_branches)
    elif args.format_string:
        for branch in managed_review_branches:
            print args.format_string.format(**branch)
    else:  # args.format_summary
        if managed_review_branches:
            print "{:6} {:14} {}".format("ID", "status", "tracked name")
            for branch in managed_review_branches:
                print "{review_id:6} {status:14} {tracked_name}".format(
                    **branch)


def _remote_branches_as_short_local(hash_ref_pairs, remote):

    def is_remote(ref):
        return phlgitu_ref.is_under_remote(ref, remote)

    full_to_short = phlgitu_ref.fq_remote_to_short_local
    branch_to_hash = dict([
        (full_to_short(r), h) for h, r in hash_ref_pairs if is_remote(r)
    ])

    return branch_to_hash


def _short_local_branches(hash_ref_pairs):

    is_local_branch = phlgitu_ref.is_fq_local_branch
    full_to_short = phlgitu_ref.fq_to_short
    branch_to_hash = dict([
        (full_to_short(r), h) for h, r in hash_ref_pairs if is_local_branch(r)
    ])

    return branch_to_hash


def _get_managed_review_branches(remote_branch_to_hash, branch_pairs):
    managed_review_branches = []
    for pair in branch_pairs:
        if pair.tracker:
            user_commit = remote_branch_to_hash.get(
                pair.tracker.review_name, None)

            branch = {
                'review_id': pair.tracker.id,
                'status': pair.tracker.status,
                'description': pair.tracker.description,
                'tracked_name': pair.tracker.review_name,
                'remote': pair.tracker.remote,
                'remote_base': pair.tracker.remote_base,
                'remote_branch': pair.tracker.remote_branch,
                'base': pair.tracker.base,
                'branch': pair.tracker.branch,
                'review_commit': remote_branch_to_hash[pair.tracker.branch],
                'user_commit': user_commit,
            }
            managed_review_branches.append(branch)
    return managed_review_branches


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
# ------------------------------ END-OF-FILE ----------------------------------
