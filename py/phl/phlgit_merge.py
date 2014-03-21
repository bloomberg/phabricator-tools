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


#------------------------------------------------------------------------------
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
#------------------------------- END-OF-FILE ----------------------------------
