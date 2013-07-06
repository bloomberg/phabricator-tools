"""Abstraction for Arcyd's git operations."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_git
#
# Public Classes:
#   Clone
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import phlgit_branch
import phlgit_checkout
import phlgit_config
import phlgit_diff
import phlgit_log
import phlgit_merge
import phlgit_push


class Clone(object):

    def __init__(self, clone):
        """Initialise a new Clone.

        :clone: a phlsys_git.Clone to delegate to
        :returns: None

        """
        super(Clone, self).__init__()
        self._clone = clone

    def is_identical(self, branch1, branch2):
        """Return True if the branches point to the same commit.

        :branch1: string name of branch
        :branch2: string name of branch
        :returns: True if the branches point to the same commit

        """
        return phlgit_branch.is_identical(self._clone, branch1, branch2)

    # TODO: internalize 'remote' to remove this parameter
    def get_remote_branches(self, remote):
        """Return a list of string names of remote branches.

        :remote: string name of remote to query
        :returns: list of string names

        """
        return phlgit_branch.get_remote(self._clone, remote)

    def checkout_forced_new_branch(self, new_name, based_on):
        """Overwrite and checkout 'new_name' as a new branch from 'based_on'.

        :new_name: the string name of the branch to create and overwrite
        :based_on: the string name of the branch to copy
        :returns: None

        """
        phlgit_checkout.new_branch_force_based_on(
            self._clone, new_name, based_on)

    # TODO: split this into more functions with varying context
    def raw_diff_range(self, base, to, context=None):
        """Return a string of the unified diff between 'base' and 'to'.

        Note that the output is based on 'git diff base...to', so the commits
        are diff'ed via thier common ancestry.

        :base: the commit or branch name to start from
        :to: the commit or branch name to end with
        :context: integer amount of surrounding context to include
        :returns: string of the unified diff

        """
        return phlgit_diff.raw_diff_range(self._clone, base, to, context)

    def get_range_hashes(self, start, end):
        """Return a list of strings of commit hashes from 'start' to 'end'.

        The list begins with the revision closest to but not including
        'start'.  Raise a ValueError if any of the returned values are not
        valid hexadecimal.

        :start: a reference that log will understand
        :end: a reference that log will understand
        :returns: a list of strings of commit hashes from 'start' to 'end'.

        """
        return phlgit_log.get_range_hashes(self._clone, start, end)

    def make_revisions_from_hashes(self, hashes):
        """Return a list of 'phlgit_log__Revision' from 'hashes'.

        Raise an exception if the clone does not return a valid FullMessage
        from any of 'hashes'.

        :hashes: a list of commit hash strings
        :returns: a list of 'phlgit_log__Revision'

        """
        return phlgit_log.make_revisions_from_hashes(self._clone, hashes)

    def squash_merge(self, branch, message, author_name, author_email):
        """Return output from Git performing a squash merge.

        :branch: string name of branch to merge into HEAD
        :message: string message for the merge commit
        :author_name: string name of author for the merge commit
        :author_email: string email of author for the merge commit
        :returns: string of Git output

        """
        # TODO: test that the author is set correctly
        return phlgit_merge.squash(
            self._clone,
            branch,
            message,
            author_name + " <" + author_email + ">")

    # TODO: internalize 'remote' to remove this parameter
    def push_asymmetrical(self, local_branch, remote_branch, remote):
        """Push 'local_branch' as 'remote_branch' to 'remote'.

        :local_branch: string name of the branch to push
        :remote_branch: string name of the branch on the remote
        :remote: string name of the remote
        :returns: None

        """
        phlgit_push.push_asymmetrical(
            self._clone, local_branch, remote_branch, remote)

    # TODO: internalize 'remote' to remove this parameter
    def push(self, branch, remote):
        """Push 'branch' to 'remote'.

        :branch: string name of the branch to push
        :remote: string name of the remote
        :returns: None

        """
        phlgit_push.push(self._clone, branch, remote)

    # TODO: internalize 'remote' to remove this parameter
    def delete(self, branch, remote):
        """Delete 'branch' from the specified remote.

        :branch: string name of the branch
        :remote: string name of the remote
        :returns: None

        """
        phlgit_push.delete(self._clone, branch, remote)

    def set_name_email(self, name, email):
        """Return output from Git performing a squash merge.

        :name: string name of author
        :email: string email of author
        :returns: None

        """
        phlgit_config.set_username_email(self._clone, name, email)

    def call(self, *args, **kwargs):
        return self._clone.call(*args, **kwargs)


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
