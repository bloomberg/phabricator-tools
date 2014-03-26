"""Abstraction for Arcyd's git operations."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_git
#
# Public Classes:
#   Repo
#    .is_identical
#    .get_remote_branches
#    .checkout_forced_new_branch
#    .raw_diff_range
#    .get_range_hashes
#    .make_revisions_from_hashes
#    .squash_merge
#    .archive_to_landed
#    .push_landed
#    .archive_to_abandoned
#    .push_abandoned
#    .push_asymmetrical
#    .push
#    .push_delete
#    .fetch_prune
#    .hash_ref_pairs
#    .get_remote
#
# Public Functions:
#   get_managed_branches
#
# Public Assignments:
#   ARCYD_LANDED_REF
#   ARCYD_LANDED_BRANCH_FQ
#   ARCYD_ABANDONED_REF
#   ARCYD_ABANDONED_BRANCH_FQ
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
from __future__ import absolute_import

import phlgit_branch
import phlgit_checkout
import phlgit_commit
import phlgit_diff
import phlgit_fetch
import phlgit_log
import phlgit_merge
import phlgit_push
import phlgit_showref
import phlgitu_ref
import phlgitx_refcache

import abdt_branch
import abdt_lander
import abdt_logging
import abdt_naming

_LANDED_ARCHIVE_BRANCH_MESSAGE = """
Create an archive branch for landed branches

Landed branches will be automatically merged here by Arcyd for your
reference.

This branch is useful for:

  o: cleaning up branches contained by the landed branch
     (see 'git branch --merged')

  o: finding the pre-landed version of a commit
     (see 'git log --grep' - you can search for the landed sha1)

  o: keeping track of Arcyd's landing activity
     (see 'git log --first-parent')

""".strip()

ARCYD_LANDED_REF = "refs/arcyd/landed"
_ARCYD_LANDED_BRANCH = "__private_arcyd/landed"
ARCYD_LANDED_BRANCH_FQ = "refs/heads/" + _ARCYD_LANDED_BRANCH

_ABANDONED_ARCHIVE_BRANCH_MESSAGE = """
Create an archive branch for abandoned branches

Abandoned branches will be automatically merged here by Arcyd for your
reference.

This branch is useful for:

  o: keeping track of Arcyd's abandoning activity
     (see 'git log --first-parent')

  o: recovering abandoned branches
     (use 'git branch <branch name> <commit hash>')

""".strip()

ARCYD_ABANDONED_REF = "refs/arcyd/abandoned"
_ARCYD_ABANDONED_BRANCH = "__private_arcyd/abandoned"
ARCYD_ABANDONED_BRANCH_FQ = "refs/heads/" + _ARCYD_ABANDONED_BRANCH


class Repo(object):

    def __init__(
            self, repo, remote, description):
        """Initialise a new Repo.

        :repo: a callable supporting git commands, e.g. repo("status")
        :remote: name of the remote to use
        :description: short identification of the repo for humans
        :returns: None

        """
        super(Repo, self).__init__()
        self._repo = phlgitx_refcache.Repo(repo)
        self._remote = remote
        self._description = description
        self._is_landing_archive_enabled = None

    def is_identical(self, branch1, branch2):
        """Return True if the branches point to the same commit.

        :branch1: string name of branch
        :branch2: string name of branch
        :returns: True if the branches point to the same commit

        """
        return phlgit_branch.is_identical(self, branch1, branch2)

    def _is_ref(self, ref):
        """Return True if the specified ref exists, otherwise False.

        :ref: the string name of the ref to look up
        :return: True if the specified ref exists, otherwise False

        """
        ref_names = phlgit_showref.names(self)
        return ref in ref_names

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

        Raise an exception if the repo does not return a valid FullMessage
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

    def _checkout_archive_ref_branch(
            self, short_branch_name, fq_branch_name, initial_message):

        if self._is_ref(fq_branch_name):
            phlgit_checkout.branch(self, short_branch_name)
        else:
            phlgit_checkout.orphan_clean(self, short_branch_name)
            phlgit_commit.allow_empty(self, initial_message)

    def archive_to_landed(
            self, review_hash, review_branch, base_branch, land_hash, message):
        """Merge the specified review branch to the 'landed' archive branch.

        :review_hash: the string of the commit hash to archive
        :review_branch: the string name of the branch to archive
        :base_branch: the string name of the branch the review is branched off
        :land_hash: the string of the commit hash the branch landed with
        :message: the string commit message the the branch landed with
        :returns: None

        """
        self._checkout_archive_ref_branch(
            _ARCYD_LANDED_BRANCH,
            ARCYD_LANDED_BRANCH_FQ,
            _LANDED_ARCHIVE_BRANCH_MESSAGE)

        new_message = "landed {} on {} as {}\n\nwith message:\n{}".format(
            review_branch, base_branch, land_hash, message)

        phlgit_merge.ours(self, review_hash, new_message)

    def push_landed(self):
        """Push the 'landed' archive branch to the remote.

        :returns: None

        """
        self.push_asymmetrical(ARCYD_LANDED_BRANCH_FQ, ARCYD_LANDED_REF)

    def archive_to_abandoned(
            self, review_hash, review_branch, base_branch):
        """Merge the specified review branch to the 'abandoned' archive branch.

        :review_hash: the string of the commit hash to archive
        :review_branch: the string name of the branch to archive
        :base_branch: the string name of the branch the review is branched off
        :returns: None

        """
        # get on the archive branch, create new orphan if necessary
        self._checkout_archive_ref_branch(
            _ARCYD_ABANDONED_BRANCH,
            ARCYD_ABANDONED_BRANCH_FQ,
            _ABANDONED_ARCHIVE_BRANCH_MESSAGE)

        new_message = "abandoned {}, branched from {}".format(
            review_branch, base_branch)

        phlgit_merge.ours(self, review_hash, new_message)

    def push_abandoned(self):
        """Push the 'abandoned' archive branch to the remote.

        :returns: None

        """
        self.push_asymmetrical(
            ARCYD_ABANDONED_BRANCH_FQ, ARCYD_ABANDONED_REF)

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

    def fetch_prune(self):
        """Fetch from the remote and prune branches.

        :returns: None

        """
        phlgit_fetch.prune_safe(self, self._remote)

    @property
    def hash_ref_pairs(self):
        """Return a list of (sha1, name) tuples from the repo's list of refs.

        :repo: a callable supporting git commands, e.g. repo("status")
        :returns: a list of (sha1, name)

        """
        return self._repo.hash_ref_pairs

    def __call__(self, *args, **kwargs):
        if args and args[0] == 'push':
            abdt_logging.on_io_event(
                'git-push',
                '{}: {} {}'.format(
                    self._description, ' '.join(args), kwargs))
        return self._repo(*args, **kwargs)

    def get_remote(self):
        return self._remote


def _get_branch_to_hash(git):

    remote = git.get_remote()
    hash_ref_list = git.hash_ref_pairs

    def is_remote(ref):
        return phlgitu_ref.is_under_remote(ref, remote)

    # XXX: can't use dictionary comprehensions until the linters don't complain
    full_to_short = phlgitu_ref.fq_remote_to_short_local
    branch_to_hash = dict([
        (full_to_short(r), h) for h, r in hash_ref_list if is_remote(r)
    ])

    return branch_to_hash


def get_managed_branches(git, repo_desc, naming, branch_link_callable=None):
    branch_to_hash = _get_branch_to_hash(git)
    branch_pairs = abdt_naming.get_branch_pairs(branch_to_hash.keys(), naming)

    managed_branches = []
    lander = abdt_lander.squash

    for b in branch_pairs:
        branch_url = None
        review_branch = b.review
        tracker_branch = b.tracker
        assert review_branch is not None or tracker_branch is not None

        review_hash = None
        tracker_hash = None

        if review_branch is not None:
            review_hash = branch_to_hash[review_branch.branch]
            if branch_link_callable:
                branch_url = branch_link_callable(review_branch.branch)

        if tracker_branch is not None:
            tracker_hash = branch_to_hash[tracker_branch.branch]

        managed_branches.append(
            abdt_branch.Branch(
                git,
                review_branch,
                review_hash,
                tracker_branch,
                tracker_hash,
                lander,
                repo_desc,
                branch_url))

    return managed_branches


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
