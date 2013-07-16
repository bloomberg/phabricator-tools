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
import phlgitu_ref
import phlsys_fs
import phlsys_git
import phlsys_subprocess

import abdt_exception
import abdt_gittypes
import abdt_naming
import abdt_workingbranch

_MAX_DIFF_SIZE = 1.5 * 1024 * 1024
_DIFF_CONTEXT_LINES = 1000
_LESS_DIFF_CONTEXT_LINES = 100


class Clone(object):

    def __init__(self, working_dir, remote):
        """Initialise a new Clone.

        :clone: a phlsys_git.Clone to delegate to
        :returns: None

        """
        super(Clone, self).__init__()
        self._clone = phlsys_git.GitClone(working_dir)
        self._remote = remote

    def is_identical(self, branch1, branch2):
        """Return True if the branches point to the same commit.

        :branch1: string name of branch
        :branch2: string name of branch
        :returns: True if the branches point to the same commit

        """
        return phlgit_branch.is_identical(self._clone, branch1, branch2)

    def get_remote_branches(self):
        """Return a list of string names of remote branches.

        :returns: list of string names

        """
        return phlgit_branch.get_remote(self._clone, self._remote)

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

    def push_asymmetrical(self, local_branch, remote_branch):
        """Push 'local_branch' as 'remote_branch' to the remote.

        :local_branch: string name of the branch to push
        :remote_branch: string name of the branch on the remote
        :returns: None

        """
        phlgit_push.push_asymmetrical(
            self._clone, local_branch, remote_branch, self._remote)

    def push(self, branch):
        """Push 'branch' to the remote.

        :branch: string name of the branch to push
        :returns: None

        """
        phlgit_push.push(self._clone, branch, self._remote)

    def push_delete(self, branch):
        """Delete 'branch' from the remote.

        :branch: string name of the branch
        :returns: None

        """
        phlgit_push.delete(self._clone, branch, self._remote)

    def set_name_email(self, name, email):
        """Return output from Git performing a squash merge.

        :name: string name of author
        :email: string email of author
        :returns: None

        """
        phlgit_config.set_username_email(self._clone, name, email)

    def call(self, *args, **kwargs):
        return self._clone.call(*args, **kwargs)

    def get_remote(self):
        return self._remote

    def get_managed_branches(self):
        remote_branches = self.get_remote_branches()
        wbList = abdt_naming.getWorkingBranches(remote_branches)
        makeRb = abdt_naming.makeReviewBranchNameFromWorkingBranch
        rbDict = dict((makeRb(wb), wb) for wb in wbList)

        managed_branches = []
        self._add_abandoned_branches(managed_branches, remote_branches, wbList)
        self._add_paired_branches(managed_branches, remote_branches, rbDict)
        return managed_branches

    def _add_abandoned_branches(
            self, abandoned_list, branches, working_branches):
        for b in working_branches:
            rb = abdt_naming.makeReviewBranchNameFromWorkingBranch(b)
            if rb not in branches:
                working_branch = abdt_gittypes.makeGitWorkingBranch(
                    b, self._remote)
                abandoned_list.append(
                    _ManagedBranch(self, None, working_branch))

    def _add_paired_branches(
            self, paired, branches, rb_to_wb):
        for b in branches:
            if abdt_naming.isReviewBranchPrefixed(b):
                review_branch = abdt_naming.makeReviewBranchFromName(b)
                if review_branch is None:
                    # TODO: handle this case properly
                    continue

                review_branch = abdt_gittypes.makeGitReviewBranch(
                    review_branch, self._remote)
                working_branch = None
                if b in rb_to_wb.keys():
                    working_branch = rb_to_wb[b]
                    working_branch = abdt_gittypes.makeGitWorkingBranch(
                        working_branch, self._remote)

                paired.append(
                    _ManagedBranch(self, review_branch, working_branch))


class _ManagedBranch(object):

    def __init__(self, clone, review_branch, tracking_branch):
        self._clone = clone
        self._review_branch = review_branch
        self._tracking_branch = tracking_branch

    def is_abandoned(self):
        return not self._review_branch and self._tracking_branch

    def is_null(self):
        return not self._review_branch and not self._tracking_branch

    def is_new(self):
        return self._review_branch and not self._tracking_branch

    def base_branch_name(self):
        if self._review_branch:
            return self._review_branch.base
        return self._tracking_branch.base

    def review_branch_name(self):
        if self._review_branch:
            return self._review_branch.branch
        return abdt_naming.makeReviewBranchNameFromWorkingBranch(
            self._tracking_branch)

    def tracking_branch_name(self):
        return self._tracking_branch.branch

    def review_id_or_none(self):
        if not self._tracking_branch:
            return None

        review_id = None
        try:
            review_id = int(self._tracking_branch.id)
        except ValueError:
            pass

        return review_id

    def review_branch(self):
        return self._review_branch

    def tracking_branch(self):
        return self._tracking_branch

    def is_status_bad_pre_review(self):
        return self._tracking_branch and abdt_naming.isStatusBadPreReview(
            self._tracking_branch)

    def is_status_bad_land(self):
        return self._tracking_branch and abdt_naming.isStatusBadLand(
            self._tracking_branch)

    def is_status_bad(self):
        return self._tracking_branch and abdt_naming.isStatusBad(
            self._tracking_branch)

    def has_new_commits(self):
        return not phlgit_branch.is_identical(
            self._clone,
            self._review_branch.remote_branch,
            self._tracking_branch.remote_branch)

    def push_delete_tracking_branch(self):
        self._clone.push_delete(self.tracking_branch_name())

    def push_bad_land(self):
        context = abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), None)
        abdt_workingbranch.pushBadLand(
            context, self.review_branch(), self.tracking_branch())

    def push_bad_in_review(self):
        context = abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), None)
        abdt_workingbranch.pushBadInReview(
            context, self.review_branch(), self.tracking_branch())

    def push_new_bad_in_review(self, review_id):
        context = abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), None)
        wb = abdt_gittypes.makeGitWorkingBranchFromParts(
            abdt_naming.WB_STATUS_BAD_INREVIEW,
            self._review_branch.description,
            self._review_branch.base,
            review_id,
            context.remote)
        self._tracking_branch = wb
        self.push_bad_in_review()

    def push_bad_pre_review(self):
        context = abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), None)
        abdt_workingbranch.pushBadPreReview(context, self._review_branch)

    def push_status(self, status):
        context = abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), None)
        self._tracking_branch = abdt_workingbranch.pushStatus(
            context,
            self._review_branch,
            self._tracking_branch,
            status)

    def push_ok_new_review(self, revision_id):
        self._tracking_branch = abdt_naming.makeWorkingBranchName(
            abdt_naming.WB_STATUS_OK,
            self._review_branch.description,
            self._review_branch.base,
            revision_id)
        self._tracking_branch = abdt_naming.makeWorkingBranchFromName(
            self._tracking_branch)
        self._tracking_branch = abdt_gittypes.makeGitWorkingBranch(
            self._tracking_branch, self._clone.get_remote())
        self._clone.push_asymmetrical(
            self._review_branch.remote_branch,
            phlgitu_ref.make_local(self.tracking_branch_name()))

    def get_author_names_emails(self):
        hashes = self.get_commit_hashes()
        return phlgit_log.get_author_names_emails_from_hashes(
            self._clone, hashes)

    def get_any_author_emails(self):
        if phlgitu_ref.parse_ref_hash(
                self._clone, self._review_branch.remote_base) is None:
            hashes = phlgit_log.get_last_n_commit_hashes_from_ref(
                self._clone, 1, self._review_branch.remote_branch)
        else:
            # TODO: use get_commit_hashes() instead, when non-raising
            hashes = self._clone.get_range_hashes(
                self._review_branch.remote_base,
                self._review_branch.remote_branch)

        if not hashes:
            hashes = phlgit_log.get_last_n_commit_hashes_from_ref(
                self._clone, 1, self._review_branch.remote_branch)
        committers = phlgit_log.get_author_names_emails_from_hashes(
            self._clone, hashes)
        emails = [committer[1] for committer in committers]
        return emails

    def get_commit_hashes(self):
        hashes = self._clone.get_range_hashes(
            self._review_branch.remote_base,
            self._review_branch.remote_branch)
        # TODO: this doesn't belong here, move up and out
        if not hashes:
            raise abdt_exception.AbdUserException("no history to diff")
        return hashes

    def make_message_digest(self):
        hashes = self.get_commit_hashes()
        revisions = self._clone.make_revisions_from_hashes(hashes)
        message = revisions[0].subject + "\n\n"
        for r in revisions:
            message += r.message
        return message

    def make_raw_diff_with_context(self, context=None):
        return self._clone.raw_diff_range(
            self._review_branch.remote_base,
            self._review_branch.remote_branch,
            context)

    def make_raw_diff(self):
        rawDiff = self.make_raw_diff_with_context(_DIFF_CONTEXT_LINES)

        if not rawDiff:
            raise abdt_exception.AbdUserException(
                str(
                    "no difference from "
                    + self._review_branch.base
                    + " to "
                    + self._review_branch.branch))

        # if the diff is too big then regen with less context
        if len(rawDiff) >= _MAX_DIFF_SIZE:
            rawDiff = self.make_raw_diff_with_context(_LESS_DIFF_CONTEXT_LINES)

        # if the diff is still too big then regen with no context
        if len(rawDiff) >= _MAX_DIFF_SIZE:
            rawDiff = self.make_raw_diff_with_context()

        # if the diff is still too big then error
        if len(rawDiff) >= _MAX_DIFF_SIZE:
            raise abdt_exception.LargeDiffException(
                "diff too big", len(rawDiff), _MAX_DIFF_SIZE)

    def _is_based_on(self, name, base):
        # TODO: actually do this
        return True

    def verify_review_branch_base(self):
        if self._review_branch.base not in self._clone.get_remote_branches():
            raise abdt_exception.MissingBaseException(
                self._review_branch.branch, self._review_branch.base)
        if not self._is_based_on(
                self._review_branch.branch, self._review_branch.base):
            raise abdt_exception.AbdUserException(
                "'" + self._review_branch.branch +
                "' is not based on '" + self._review_branch.base + "'")

    def land(self, author_name, author_email, message):
        self._clone.checkout_forced_new_branch(
            self._tracking_branch.base,
            self._tracking_branch.remote_base)

        try:
            with phlsys_fs.nostd():
                result = self._clone.squash_merge(
                    self._tracking_branch.remote_branch,
                    message,
                    author_name,
                    author_email)
        except phlsys_subprocess.CalledProcessError as e:
            self._clone.call("reset", "--hard")  # fix the working copy
            raise abdt_exception.LandingException(
                '\n' + e.stdout,
                self.review_branch_name(),
                self._tracking_branch.base)

        self._clone.push(self._tracking_branch.base)
        self._clone.push_delete(self._tracking_branch.branch)
        self._clone.push_delete(self.review_branch_name())

        return result

    def make_revision_from_tip(self):
        hashes = self.get_commit_hashes()
        return phlgit_log.make_revision_from_hash(self._clone, hashes[-1])


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
