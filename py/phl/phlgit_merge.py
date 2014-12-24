"""Wrapper around 'git merge'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_merge
#
# Public Classes:
#   MergeException
#
# Public Functions:
#   squash
#   ours
#   no_ff
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
# TODO: write test driver
# TODO: distinguish between different error conditions

from __future__ import print_function
from __future__ import absolute_import

import phlsys_fs
import phlsys_subprocess


class MergeException(Exception):

    def __init__(self, description):
        super(MergeException, self).__init__(description)


def squash(repo, source, message, author=None):
    # TODO: test merging with no effective changes
    with phlsys_fs.nostd():
        try:
            repo("merge", "--squash", source)
            if author:
                result = repo(
                    "commit", "-m", message, "--author", author)
            else:
                result = repo("commit", "-m", message)
        except phlsys_subprocess.CalledProcessError as e:
            raise MergeException(e.stdout)

    return result


def ours(repo, branch, message):
    """Merge the specified 'branch' into HEAD, discarding all changes.

    There can be no merge conflicts with this merge as no integration of
    changes is actually performed, the resulting tree will be the same
    as HEAD.

    Behaviour is undefined if the current branch is 'branch'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :branch: the string name of the branch to merge into HEAD
    :message: the string message to make on the commit
    :returns: None

    """
    return repo("merge", "--no-edit", "-s", "ours", branch, "-m", message)


def no_ff(repo, branch):
    """Merge the single 'branch' into HEAD.

    Behaviour is undefined if there are merge conflicts.
    Behaviour is undefined if the current branch is 'branch'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :branch: the single branch to merge
    :returns: None

    """
    repo('merge', '--no-edit', branch)


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
