"""Wrapper around 'git push'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_push
#
# Public Functions:
#   push_asymmetrical_force
#   push_asymmetrical
#   push
#   force_branch
#   branch
#   move_asymmetrical
#   delete
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import itertools


def push_asymmetrical_force(repo, localBranch, remoteBranch, remoteName):
    repo('push', remoteName, localBranch + ":" + remoteBranch, "--force")


def push_asymmetrical(repo, localBranch, remoteBranch, remoteName):
    repo('push', remoteName, localBranch + ":" + remoteBranch)


def push(repo, branch, remoteName):
    repo('push', remoteName, branch)


def force_branch(repo, branch, remote='origin'):
    """Force push 'branch' to the supplied 'origin'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :branch: the string name of the branch to push
    :remote: the string name of the remote to push to
    :returns: None

    """
    repo('push', '--force', remote, branch)


def branch(repo, branch, remote='origin'):
    repo('push', remote, branch)


def move_asymmetrical(repo, local_branch, old_remote, new_remote, remote):
    """Delete 'old_remote', push 'local_branch' to 'new_remote' on 'remote'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :local_branch: the local reference to push
    :old_remote: the old reference on the remote to delete
    :new_remote: the new reference on the remote to push to
    :remote: the name of the remote to push to
    :returns: None

    """
    repo(
        'push',
        remote,
        local_branch + ":" + new_remote,
        ":" + old_remote)


def delete(repo, remote, branch, *args):
    """Delete 'branch' from the specified remote.

    :repo: a callable supporting git commands, e.g. repo("status")
    :remote: string name of the remote
    :branch: string name of the branch
    :*args: (optional) more string names of branches
    :returns: None

    """
    removals = [':' + b for b in itertools.chain([branch], args)]
    repo('push', remote, *removals)

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
