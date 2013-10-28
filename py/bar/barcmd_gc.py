"""Garbage collect in your local git repository.

Will safely clean up local branches which have already been landed.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# barcmd_gc
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#   get_current_branch
#   prune_force
#   prune_dryrun
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import sys

import abdt_landinglog
import phlgit_branch
import phlsys_choice
import phlsys_git


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    force_or_dryrun_group = parser.add_argument_group(
        "choose either force or dry-run")
    force_or_dryrun = force_or_dryrun_group.add_mutually_exclusive_group(
        required=True)
    force_or_dryrun.add_argument(
        '--force', '-f',
        action='store_true',
        help='actually perform the removals')
    force_or_dryrun.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='preview what would be done if you specify --force')

    parser.add_argument(
        '--aggressive', '-a',
        action='store_true',
        help='aggressively remove branches')


def process(args):
    clone = phlsys_git.GitClone('.')

    fetch_urls = clone.call(
        'config', '--get-all', 'remote.origin.fetch').splitlines()

    landinglog_ref = 'refs/arcyd/landinglog'
    landinglog_fetch = '+refs/arcyd/landinglog:refs/arcyd/origin/landinglog'
    if landinglog_fetch not in fetch_urls:
        remote_refs = clone.call('ls-remote').split()[1::2]
        if landinglog_ref not in remote_refs:
            print >> sys.stderr, str(
                "FATAL: this repo doesn't seem to have a landing log yet "
                "perhaps it's not managed by arcyd or no branches have ever "
                "been landed.")
            return 1

        print "this repo doesn't seem to be set up to fetch the landing log."
        choice = phlsys_choice.yes_or_no_or_abort(
            "would you like to set this up now and fetch origin?")
        if choice is None:
            print 'aborting.'
            return 1
        elif choice:
            clone.call(
                'config', '--add', 'remote.origin.fetch', landinglog_fetch)
            print 'set up to fetch landinglog, fetching ...'
            clone.call('fetch')
            print 'fetched.'
        else:
            print 'continuing without setting up to fetch landinglog.'

    log = abdt_landinglog.get_log(clone)
    log_dict = {i.review_sha1: (i.name, i.landed_sha1) for i in log}

    current_branch = get_current_branch(clone)

    if args.force:
        prune_func = prune_force
    else:
        assert args.dry_run
        prune_func = prune_dryrun

    local_branches = phlgit_branch.get_local_with_sha1(clone)

    did_something = False
    for branch in local_branches:
        sha1 = branch[0]
        if sha1 in log_dict:
            local_name = branch[1]
            log_data = log_dict[sha1]
            original_name = log_data[0]
            landed_sha1 = log_data[1]
            if local_name == current_branch:
                print >> sys.stderr, str(
                    "cannot prune {}, it's the current branch").format(
                        current_branch)
            elif local_name == original_name or args.aggressive:
                prune_func(clone, local_name, original_name, sha1, landed_sha1)
                did_something = True
            else:
                print "not pruning '{}', matches landed '{}'".format(
                    local_name, original_name)
                print "use '--aggressive' to remove"

    if not did_something:
        print "nothing to do."


def get_current_branch(clone):
    head = clone.call('symbolic-ref', 'HEAD')
    branch_prefix = 'refs/heads/'
    current_branch = None
    if head.startswith(branch_prefix):
        current_branch = head[len(branch_prefix):].strip()
    return current_branch


def prune_force(clone, local_name, original_name, sha1, landed_sha1):
    if local_name == original_name:
        print "pruning '{}' ({}), landed as ({})".format(
            local_name, sha1, landed_sha1)
        clone.call('branch', '-D', local_name)
    else:
        print "pruning '{}' ({}), matches landed {} ({})".format(
            local_name, sha1, original_name, landed_sha1)
        clone.call('branch', '-D', local_name)


def prune_dryrun(clone, local_name, original_name, sha1, landed_sha1):
    _ = clone  # NOQA
    if local_name == original_name:
        print "would prune '{}' ({}), landed as ({})".format(
            local_name, sha1, landed_sha1)
    else:
        print "would prune '{}' ({}), matches landed {} ({})".format(
            local_name, sha1, original_name, landed_sha1)


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
