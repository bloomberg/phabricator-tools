"""Wrapper around 'git checkout'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_checkout
#
# Public Functions:
#   new_branch_force_based_on
#   branch
#   previous_branch
#   orphan
#   orphan_clean
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def new_branch_force_based_on(repo, new_branch, base):
    """Checkout onto a new branch copy of base, overwite existing branch.

    :repo: a callable supporting git commands, e.g. repo("status")
    :new_branch: the name for the new branch
    :base: the name of the branch to copy
    :returns: None

    """
    repo('checkout', '-B', new_branch, base)


def branch(repo, branch):
    """Checkout onto an existing branch.

    Note that the existing branch may be on a remote, in which case a tracking
    branch will be set up.

    :repo: a callable supporting git commands, e.g. repo("status")
    :branch: the string name of the branch
    :returns: None

    """
    repo('checkout', branch)


def previous_branch(repo):
    """Checkout onto the branch the repo was on before this one.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: None

    """
    repo('checkout', '-')


def orphan(repo, branch):
    """Checkout onto a new branch with no history.

    Note that the working tree will not be empty and will contain whatever
    was at the last commit.

    Note that the specified 'branch' must not exist before.

    :repo: a callable supporting git commands, e.g. repo("status")
    :branch: the string name of the branch
    :returns: None

    """
    repo('checkout', '--orphan', branch)


def orphan_clean(repo, branch):
    """Checkout onto a new branch with no history and an empty working tree.

    This is different from a pure 'orphan checkout' in that the working
    tree is deliberately emptied.

    Note that the specified 'branch' must not exist before.

    :repo: a callable supporting git commands, e.g. repo("status")
    :branch: the string name of the branch
    :returns: None

    """
    orphan(repo, branch)

    # remove any files that have followed us from the previous branch in the
    # index
    files = repo('ls-files', '--cached')
    if files:
        repo('rm', '--cached', '-rf', '--', '.')

    # any removed files will now be in the working copy, note that some files
    # may be both previously managed and ignored, so it's important to use
    # the 'x' too.
    repo('clean', '-fxd')


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
