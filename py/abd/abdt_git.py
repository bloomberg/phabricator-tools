"""Abstraction for Arcyd's git operations."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_git
#
# Public Classes:
#   Clone
#    .is_identical
#    .get_remote_branches
#    .checkout_forced_new_branch
#    .raw_diff_range
#    .get_range_hashes
#    .make_revisions_from_hashes
#    .squash_merge
#    .push_asymmetrical
#    .push
#    .push_delete
#    .set_name_email
#    .call
#    .get_remote
#    .working_dir
#
# Public Functions:
#   get_managed_branches
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
from __future__ import absolute_import

import phlgit_branch
import phlgit_checkout
import phlgit_config
import phlgit_diff
import phlgit_log
import phlgit_merge
import phlgit_push

import abdt_branch
import abdt_lander
import abdt_logging
import abdt_naming


class Clone(object):

    def __init__(
            self, clone, remote, description):
        """Initialise a new Clone.

        :clone: the clone to attach to and delegate calls to
        :remote: name of the remote to use
        :description: short identification of the repo for humans
        :returns: None

        """
        super(Clone, self).__init__()
        self._clone = clone
        self._remote = remote
        self._description = description

    def is_identical(self, branch1, branch2):
        """Return True if the branches point to the same commit.

        :branch1: string name of branch
        :branch2: string name of branch
        :returns: True if the branches point to the same commit

        """
        return phlgit_branch.is_identical(self, branch1, branch2)

    def get_remote_branches(self):
        """Return a list of string names of remote branches.

        :returns: list of string names

        """
        return phlgit_branch.get_remote(self, self._remote)

    def checkout_forced_new_branch(self, new_name, based_on):
        """Overwrite and checkout 'new_name' as a new branch from 'based_on'.

        :new_name: the string name of the branch to create and overwrite
        :based_on: the string name of the branch to copy
        :returns: None

        """
        phlgit_checkout.new_branch_force_based_on(
            self, new_name, based_on)

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
        return phlgit_diff.raw_diff_range(self, base, to, context)

    def get_range_hashes(self, start, end):
        """Return a list of strings of commit hashes from 'start' to 'end'.

        The list begins with the revision closest to but not including
        'start'.  Raise a ValueError if any of the returned values are not
        valid hexadecimal.

        :start: a reference that log will understand
        :end: a reference that log will understand
        :returns: a list of strings of commit hashes from 'start' to 'end'.

        """
        return phlgit_log.get_range_hashes(self, start, end)

    def make_revisions_from_hashes(self, hashes):
        """Return a list of 'phlgit_log__Revision' from 'hashes'.

        Raise an exception if the clone does not return a valid FullMessage
        from any of 'hashes'.

        :hashes: a list of commit hash strings
        :returns: a list of 'phlgit_log__Revision'

        """
        return phlgit_log.make_revisions_from_hashes(self, hashes)

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
            self,
            branch,
            message,
            author_name + " <" + author_email + ">")

    def push_asymmetrical(self, local_branch, remote_branch):
        """Push 'local_branch' as 'remote_branch' to the remote.

        :local_branch: string name of the branch to push
        :remote_branch: string name of the branch on the remote
        :returns: None

        """
        phlgit_push.push_asymmetrical(
            self, local_branch, remote_branch, self._remote)

    def push(self, branch):
        """Push 'branch' to the remote.

        :branch: string name of the branch to push
        :returns: None

        """
        phlgit_push.push(self, branch, self._remote)

    def push_delete(self, branch, *args):
        """Delete 'branch' from the remote.

        :branch: string name of the branch
        :*args: (optional) more string names of branches
        :returns: None

        """
        phlgit_push.delete(self, self._remote, branch, *args)

    def set_name_email(self, name, email):
        """Return output from Git performing a squash merge.

        :name: string name of author
        :email: string email of author
        :returns: None

        """
        phlgit_config.set_username_email(self, name, email)

    def call(self, *args, **kwargs):
        if args and args[0] == 'push':
            abdt_logging.on_io_event(
                'git-push',
                '{}: {} {}'.format(
                    self._description, ' '.join(args), kwargs))
        return self._clone.call(*args, **kwargs)

    def get_remote(self):
        return self._remote

    @property
    def working_dir(self):
        return self._clone.working_dir


def get_managed_branches(git, repo_desc, branch_link_callable=None):
    branch_pairs = abdt_naming.get_branch_pairs(git.get_remote_branches())

    managed_branches = []
    lander = abdt_lander.squash

    for b in branch_pairs:
        branch_url = None
        review_branch = b.review
        tracker_branch = b.tracker
        assert review_branch is not None or tracker_branch is not None

        if review_branch is not None:
            if branch_link_callable:
                branch_url = branch_link_callable(review_branch.branch)

        managed_branches.append(
            abdt_branch.Branch(
                git,
                review_branch,
                tracker_branch,
                lander,
                repo_desc,
                branch_url))

    return managed_branches


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
