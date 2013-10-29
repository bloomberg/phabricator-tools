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
#   print_branch
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
    force_or_interact_group = parser.add_argument_group(
        "choose either force or interactive")

    force_or_interact = force_or_interact_group.add_mutually_exclusive_group(
        required=True)

    force_or_interact.add_argument(
        '--force', '-f',
        action='store_true',
        help='perform the removals without prompting')

    force_or_interact.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='show a summary of what would be done and ask to proceed')

    parser.add_argument(
        '--aggressive',
        action='store_true',
        help='remove branches which match landed reviews by sha1 only')

    should_update = parser.add_mutually_exclusive_group()

    should_update.add_argument(
        '--update', '-u',
        action='store_true',
        help='update landinglog without prompting')

    should_update.add_argument(
        '--no-update', '-n',
        action='store_true',
        help='dont update landinglog, dont prompt')


def process(args):
    # XXX: only supports 'origin' remote at present

    clone = phlsys_git.GitClone('.')

    _fetch_log(clone, args.update, args.no_update)

    log = abdt_landinglog.get_log(clone)
    log_dict = {i.review_sha1: (i.name, i.landed_sha1) for i in log}

    local_branches = phlgit_branch.get_local_with_sha1(clone)

    if args.force:
        did_something = _prune_branches(
            clone, args, prune_force, log_dict, local_branches)
        if not did_something:
            print "nothing to do."
        else:
            print "done."
    else:
        assert args.interactive
        would_do_something = _prune_branches(
            clone, args, prune_dryrun, log_dict, local_branches)
        if not would_do_something:
            print "nothing to do."
        else:
            choice = phlsys_choice.yes_or_no("perform the pruning?", 'no')
            print
            if choice:
                _prune_branches(
                    clone, args, prune_force, log_dict, local_branches)
                print "done."
            else:
                print "stopped."


def _fetch_log(clone, always_update, never_update):
    landinglog_ref = 'refs/arcyd/landinglog'
    local_landinglog_ref = 'refs/arcyd/origin/landinglog'
    landinglog_fetch = '+{}:{}'.format(landinglog_ref, local_landinglog_ref)

    local_refs = clone.call('show-ref').split()[1::2]
    has_landinglog = local_landinglog_ref in local_refs

    if not has_landinglog and never_update:
        print >> sys.stderr, str(
            "FATAL: the landing log has never been retrieved and "
            "'--no-update' was specified, nothing to do.")
        sys.exit(1)

    if not has_landinglog:
        # see if the remote has a landing log
        remote_refs = clone.call('ls-remote').split()[1::2]
        if landinglog_ref not in remote_refs:
            print >> sys.stderr, str(
                "FATAL: origin doesn't seem to have a landing log yet "
                "perhaps it's not managed by arcyd or no branches have ever "
                "been landed.")
            sys.exit(1)

    if not has_landinglog:
        print "fetching landing log from origin for the first time.."
        clone.call('fetch', 'origin', landinglog_fetch)
        print
    else:
        if always_update:
            print "fetching landing log from origin .."
            clone.call('fetch', 'origin', landinglog_fetch)
            print
        elif never_update:
            # nothing to do
            pass
        else:
            choice = phlsys_choice.yes_or_no_or_abort(
                "update landing log from origin now?")
            if choice is None:
                print 'aborting.'
                sys.exit(1)
            elif choice:
                print "fetching landing log from origin .."
                clone.call('fetch', 'origin', landinglog_fetch)
                print
            else:
                # they chose 'no', continue without fetching
                print


def _prune_branches(clone, args, prune_func, log_dict, local_branches):
    current_branch = get_current_branch(clone)
    did_something = False
    for branch in local_branches:
        sha1 = branch[0]
        if sha1 in log_dict:
            local_name = branch[1]
            log_data = log_dict[sha1]
            original_name = log_data[0]
            landed_sha1 = log_data[1]
            if local_name == original_name or args.aggressive:
                if local_name == current_branch:
                    err = "cannot prune {}, it's the current branch".format(
                        current_branch)
                    print >> sys.stderr, err
                    print
                else:
                    prune_func(
                        clone, local_name, original_name, sha1, landed_sha1)
                    did_something = True
            else:
                print_branch(
                    "not pruning",
                    local_name,
                    original_name,
                    sha1,
                    landed_sha1)
    return did_something


def get_current_branch(clone):
    head = clone.call('symbolic-ref', 'HEAD')
    branch_prefix = 'refs/heads/'
    current_branch = None
    if head.startswith(branch_prefix):
        current_branch = head[len(branch_prefix):].strip()
    return current_branch


def prune_force(clone, local_name, original_name, sha1, landed_sha1):
    print_branch("pruning", local_name, original_name, sha1, landed_sha1)
    clone.call('branch', '-D', local_name)


def prune_dryrun(clone, local_name, original_name, sha1, landed_sha1):
    _ = clone  # NOQA
    print_branch("would prune", local_name, original_name, sha1, landed_sha1)


def print_branch(verb_statement, local_name, original_name, sha1, landed_sha1):
    print "{} '{}'".format(verb_statement, local_name)
    print "  ({})".format(sha1)
    if local_name == original_name:
        print "  which matches landed with the same name"
        print "    ({})".format(landed_sha1)
    else:
        print "  which matches landed"
        print "    '{}'".format(original_name)
        print "    ({})".format(landed_sha1)
    print


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
