"""Dependable wrapper for invocations of git fetch."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_fetch
#
# Public Functions:
#   all_prune
#   prune_safe
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import phlsys_subprocess


def all_prune(repo):
    """Fetch from all remotes and prune dead branches.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: None

    """
    repo('fetch', '--all', '--prune')


def prune_safe(repo, remote, refspec_list=None):
    """Fetch from the specified remote and prune removed branches.

    This safely works around the case where a branch that would be fetched
    conflicts with a branch that has already been deleted, this case causes
    a straight-forward 'git fetch -p' to fail.

    e.g. given this sequence of events:

      alice $ git push origin HEAD:refs/heads/mybranch
      bob   $ git fetch -p
      alice $ git push origin :refs/heads/mybranch
      alice $ git push origin HEAD:refs/heads/mybranch/blah
      bob   $ git fetch -p

    bob would get an error when fetching the last time and would have to
    'git remote prune origin' before fetching.

    :repo: a callable supporting git commands, e.g. repo("status")
    :remote: string name of the remote to fetch from
    :refspec_list: optional list of refspecs to fetch
    :returns: None

    """
    if refspec_list is None:
        refspec_list = []
    try:
        repo('fetch', remote, '--prune', *refspec_list)
    except phlsys_subprocess.CalledProcessError:
        # assume this was due to the previously mentioned issue
        repo('remote', 'prune', remote)
        repo('fetch', remote, *refspec_list)


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
