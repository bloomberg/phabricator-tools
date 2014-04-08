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

import phlsys_subprocess


def all_prune(repo):
    """Fetch from all remotes and prune dead branches.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: None

    """
    repo('fetch', '--all', '--prune')


def prune_safe(repo, remote):
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
    :returns: None

    """
    try:
        repo('fetch', remote, '-p')
    except phlsys_subprocess.CalledProcessError:
        # assume this was due to the previously mentioned issue
        repo('remote', 'prune', remote)
        repo('fetch', remote)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
