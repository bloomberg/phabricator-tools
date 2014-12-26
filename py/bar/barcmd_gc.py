"""DEPRECATED: Garbage collect in your local git repository.

Will safely clean up local branches which have already been landed.

::DEPRECATION NOTICE::
the 'refs/arcyd/landinglog' ref is no longer being updated, for new
branches do:

    git fetch origin refs/arcyd/landed:refs/arcyd/landed
    git branch --merged refs/arcyd/landed | grep -v '*' | xargs git branch -D

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
from __future__ import division
from __future__ import print_function

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
        '--prompt-update',
        action='store_true',
        help='ask the user if landinglog should be updated')

    should_update.add_argument(
        '--update', '-u',
        action='store_true',
        help='update landinglog without prompting (default)')

    should_update.add_argument(
        '--no-update', '-n',
        action='store_true',
        help='dont update landinglog, dont prompt')


def process(args):
    # XXX: only supports 'origin' remote at present

    print("""
::DEPRECATION NOTICE::
the 'refs/arcyd/landinglog' ref is no longer being updated, for new
branches do:

    git fetch origin refs/arcyd/landed:refs/arcyd/landed
    git branch --merged refs/arcyd/landed | grep -v '*' | xargs git branch -D
    """.strip())
    print()

    repo = phlsys_git.Repo('.')

    _fetch_log(repo, args.update, args.no_update, args.prompt_update)

    log = abdt_landinglog.get_log(repo)
    log_dict = {i.review_sha1: (i.name, i.landed_sha1) for i in log}

    local_branches = phlgit_branch.get_local_with_sha1(repo)

    if args.force:
        did_something = _prune_branches(
            repo, args, prune_force, log_dict, local_branches)
        if not did_something:
            print("nothing to do.")
        else:
            print("done.")
    else:
        assert args.interactive
        would_do_something = _prune_branches(
            repo, args, prune_dryrun, log_dict, local_branches)
        if not would_do_something:
            print("nothing to do.")
        else:
            choice = phlsys_choice.yes_or_no("perform the pruning?", 'no')
            print()
            if choice:
                _prune_branches(
                    repo, args, prune_force, log_dict, local_branches)
                print("done.")
            else:
                print("stopped.")


def _fetch_log(repo, always_update, never_update, prompt_update):
    # default to always_update
    if not never_update and not prompt_update:
        always_update = True

    landinglog_ref = 'refs/arcyd/landinglog'
    local_landinglog_ref = 'refs/arcyd/origin/landinglog'
    landinglog_fetch = '+{}:{}'.format(landinglog_ref, local_landinglog_ref)

    local_refs = repo('show-ref').split()[1::2]
    has_landinglog = local_landinglog_ref in local_refs

    if not has_landinglog and never_update:
        print(str(
            "FATAL: the landing log has never been retrieved and "
            "'--no-update' was specified, nothing to do."), file=sys.stderr)
        sys.exit(1)

    if not has_landinglog:
        # see if the remote has a landing log
        remote_refs = repo('ls-remote').split()[1::2]
        if landinglog_ref not in remote_refs:
            print(str(
                "FATAL: origin doesn't seem to have a landing log yet "
                "perhaps it's not managed by arcyd or no branches have ever "
                "been landed."), file=sys.stderr)
            sys.exit(1)

    if not has_landinglog:
        print("fetching landing log from origin for the first time..")
        repo('fetch', 'origin', landinglog_fetch)
        print()
    else:
        if always_update:
            print("fetching landing log from origin ..")
            repo('fetch', 'origin', landinglog_fetch)
            print()
        elif never_update:
            # nothing to do
            pass
        else:
            assert prompt_update
            choice = phlsys_choice.yes_or_no_or_abort(
                "update landing log from origin now?")
            if choice is None:
                print('aborting.')
                sys.exit(1)
            elif choice:
                print("fetching landing log from origin ..")
                repo('fetch', 'origin', landinglog_fetch)
                print()
            else:
                # they chose 'no', continue without fetching
                print()


def _prune_branches(repo, args, prune_func, log_dict, local_branches):
    current_branch = get_current_branch(repo)
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
                    print(err, file=sys.stderr)
                    print()
                else:
                    prune_func(
                        repo, local_name, original_name, sha1, landed_sha1)
                    did_something = True
            else:
                print_branch(
                    "not pruning",
                    local_name,
                    original_name,
                    sha1,
                    landed_sha1)
    return did_something


def get_current_branch(repo):
    head = repo('symbolic-ref', 'HEAD')
    branch_prefix = 'refs/heads/'
    current_branch = None
    if head.startswith(branch_prefix):
        current_branch = head[len(branch_prefix):].strip()
    return current_branch


def prune_force(repo, local_name, original_name, sha1, landed_sha1):
    print_branch("pruning", local_name, original_name, sha1, landed_sha1)
    repo('branch', '-D', local_name)


def prune_dryrun(repo, local_name, original_name, sha1, landed_sha1):
    _ = repo  # NOQA
    print_branch("would prune", local_name, original_name, sha1, landed_sha1)


def print_branch(verb_statement, local_name, original_name, sha1, landed_sha1):
    print("{} '{}'".format(verb_statement, local_name))
    print("  ({})".format(sha1))
    if local_name == original_name:
        print("  which matches landed with the same name")
        print("    ({})".format(landed_sha1))
    else:
        print("  which matches landed")
        print("    '{}'".format(original_name))
        print("    ({})".format(landed_sha1))
    print()


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
