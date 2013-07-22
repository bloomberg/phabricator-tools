"""Implement operations for branch-based reviews."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_branch
#
# Public Classes:
#   Branch
#    .is_abandoned
#    .is_null
#    .is_new
#    .is_status_bad_pre_review
#    .is_status_bad_land
#    .is_status_bad
#    .has_new_commits
#    .base_branch_name
#    .review_branch_name
#    .review_id_or_none
#    .get_author_names_emails
#    .get_any_author_emails
#    .get_clone
#    .make_message_digest
#    .make_raw_diff
#    .verify_review_branch_base
#    .get_commit_message_from_tip
#    .abandon
#    .clear_mark
#    .mark_bad_land
#    .mark_bad_in_review
#    .mark_new_bad_in_review
#    .mark_bad_pre_review
#    .mark_ok_in_review
#    .mark_ok_new_review
#    .land
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
# TODO: write test driver

import phlgit_log
import phlgitu_ref

import abdt_differ
import abdt_exception
import abdt_gittypes
import abdt_lander
import abdt_naming
import abdt_workingbranch

# TODO: allow this to be passed in
_MAX_DIFF_SIZE = 1.5 * 1024 * 1024


class Branch(object):

    def __init__(self, clone, review_branch, tracking_branch, lander):
        """Create a new relationship tracker for the supplied branch names.

        :clone: a Git clone to delegate to
        :review_branch: the abdt_gittypes.GitReviewBranch
        :tracking_branch: the abdt_gittypes.GitWorkingBranch
        :lander: a lander conformant to abdt_lander

        """
        self._clone = clone
        self._review_branch = review_branch
        self._tracking_branch = tracking_branch
        self._lander = lander
        assert self._review_branch_valid_or_none()
        assert self._tracking_branch_valid_or_none()

    def _review_branch_valid_or_none(self):
        if not self._has_review_branch():
            return True
        else:
            return isinstance(
                self._review_branch,
                abdt_gittypes.GitReviewBranch)

    def _tracking_branch_valid_or_none(self):
        if not self._has_tracking_branch():
            return True
        else:
            return isinstance(
                self._tracking_branch,
                abdt_gittypes.GitWorkingBranch)

    def _has_review_branch(self):
        return self._review_branch is not None

    def _has_tracking_branch(self):
        return self._tracking_branch is not None

    def is_abandoned(self):
        """Return True if the author's branch no longer exists."""
        return not self._has_review_branch() and self._has_tracking_branch()

    def is_null(self):
        """Return True if we don't have any data."""
        no_review_branch = not self._has_review_branch()
        no_tracking_branch = not self._has_tracking_branch()
        return no_review_branch and no_tracking_branch

    def is_new(self):
        """Return True if we haven't marked the author's branch."""
        return self._has_review_branch() and not self._has_tracking_branch()

    def is_status_bad_pre_review(self):
        """Return True if the author's branch is marked 'bad pre-review'."""
        if self._has_tracking_branch():
            return abdt_naming.isStatusBadPreReview(self._tracking_branch)
        else:
            return False

    def is_status_bad_land(self):
        """Return True if the author's branch is marked 'bad land'."""
        if self._has_tracking_branch():
            return abdt_naming.isStatusBadLand(self._tracking_branch)
        else:
            return False

    def is_status_bad(self):
        """Return True if the author's branch is marked any bad status."""
        if self._has_tracking_branch():
            return abdt_naming.isStatusBad(self._tracking_branch)
        else:
            return False

    def has_new_commits(self):
        """Return True if the author's branch is different since marked."""
        if self.is_new():
            return True
        else:
            return not self._clone.is_identical(
                self._review_branch.remote_branch,
                self._tracking_branch.remote_branch)

    def base_branch_name(self):
        """Return the string name of the branch the review will land on."""
        if self._review_branch:
            return self._review_branch.base
        return self._tracking_branch.base

    def review_branch_name(self):
        """Return the string name of the branch the review is based on."""
        if self._review_branch:
            return self._review_branch.branch
        return abdt_naming.makeReviewBranchNameFromWorkingBranch(
            self._tracking_branch)

    def review_id_or_none(self):
        """Return the int id of the review or 'None' if there isn't one."""
        if not self._tracking_branch:
            return None

        review_id = None
        try:
            review_id = int(self._tracking_branch.id)
        except ValueError:
            pass

        return review_id

    def get_author_names_emails(self):
        """Return a list of (name, email) tuples from the branch."""
        hashes = self._get_commit_hashes()
        return phlgit_log.get_author_names_emails_from_hashes(
            self._clone, hashes)

    def get_any_author_emails(self):
        """Return a list of emails from the branch.

        If the branch has an invalid base or has no history against the base
        then resort to using the whole history.

        Useful if 'get_author_names_emails' fails.

        """
        if phlgitu_ref.parse_ref_hash(
                self._clone, self._review_branch.remote_base) is None:
            hashes = phlgit_log.get_last_n_commit_hashes_from_ref(
                self._clone, 1, self._review_branch.remote_branch)
        else:
            hashes = self._get_commit_hashes()
        if not hashes:
            hashes = phlgit_log.get_last_n_commit_hashes_from_ref(
                self._clone, 1, self._review_branch.remote_branch)
        committers = phlgit_log.get_author_names_emails_from_hashes(
            self._clone, hashes)
        emails = [committer[1] for committer in committers]
        return emails

    def get_clone(self):
        """Return the abdt_clone for this branch."""
        return self._clone

    def _get_commit_hashes(self):
        hashes = self._clone.get_range_hashes(
            self._review_branch.remote_base,
            self._review_branch.remote_branch)
        return hashes

    def make_message_digest(self):
        """Return a string digest of the commit messages on the branch.

        The digest is comprised of the title from the earliest commit
        unique to the branch and all of the message bodies from the
        unique commits on the branch.

        """
        hashes = self._get_commit_hashes()
        revisions = self._clone.make_revisions_from_hashes(hashes)
        message = revisions[0].subject + "\n\n"
        for r in revisions:
            message += r.message
        return message

    def make_raw_diff(self):
        """Return a string raw diff of the changes on the branch.

        If the diff would exceed the pre-specified max diff size then take
        measures to reduce the diff.

        """
        return abdt_differ.make_raw_diff(
            self._clone,
            self._review_branch.remote_base,
            self._review_branch.remote_branch,
            _MAX_DIFF_SIZE)

    def _is_based_on(self, name, base):
        # TODO: actually do this
        return True

    def verify_review_branch_base(self):
        """Raise exception if review branch has invalid base."""
        if self._review_branch.base not in self._clone.get_remote_branches():
            raise abdt_exception.MissingBaseException(
                self._review_branch.branch, self._review_branch.base)
        if not self._is_based_on(
                self._review_branch.branch, self._review_branch.base):
            raise abdt_exception.AbdUserException(
                "'" + self._review_branch.branch +
                "' is not based on '" + self._review_branch.base + "'")

    def get_commit_message_from_tip(self):
        """Return string commit message from latest commit on branch."""
        hashes = self._get_commit_hashes()
        revision = phlgit_log.make_revision_from_hash(self._clone, hashes[-1])
        message = revision.subject + "\n"
        message += "\n"
        message += revision.message + "\n"
        return message

    def _push_delete_tracking_branch(self):
        self._clone.push_delete(self._tracking_branch.branch)

    def abandon(self):
        """Remove information associated with the abandoned review branch."""
        # TODO: raise if the branch is not actually abandoned by the user
        self._push_delete_tracking_branch()
        self._tracking_branch = None

    def clear_mark(self):
        """Clear status and last commit associated with the review branch."""
        self._push_delete_tracking_branch()
        self._tracking_branch = None

    def mark_bad_land(self):
        """Mark the current version of the review branch as 'bad land'."""
        self._tracking_branch = abdt_workingbranch.push_bad_land(
            self._make_git_context(),
            self._review_branch,
            self._tracking_branch)

    def mark_bad_in_review(self):
        """Mark the current version of the review branch as 'bad in review'."""
        self._tracking_branch = abdt_workingbranch.push_bad_in_review(
            self._make_git_context(),
            self._review_branch,
            self._tracking_branch)

    def mark_new_bad_in_review(self, revision_id):
        """Mark the current version of the review branch as 'bad in review'."""
        self._tracking_branch = abdt_workingbranch.push_bad_new_in_review(
            self._make_git_context(),
            self._review_branch,
            revision_id)

    def mark_bad_pre_review(self):
        """Mark this version of the review branch as 'bad pre review'."""
        self._tracking_branch = abdt_workingbranch.push_bad_pre_review(
            self._make_git_context(),
            self._review_branch)

    def mark_ok_in_review(self):
        """Mark this version of the review branch as 'ok in review'."""
        self._tracking_branch = abdt_workingbranch.push_ok_in_review(
            self._make_git_context(),
            self._review_branch,
            self._tracking_branch)

    def mark_ok_new_review(self, revision_id):
        """Mark this version of the review branch as 'ok in review'."""
        self._tracking_branch = abdt_workingbranch.push_ok_new_in_review(
            self._make_git_context(),
            self._review_branch,
            revision_id)

    def land(self, author_name, author_email, message):
        """Integrate the branch into the base and remove the review branch."""
        self._clone.checkout_forced_new_branch(
            self._tracking_branch.base,
            self._tracking_branch.remote_base)

        try:
            result = self._lander(
                self._clone,
                self._tracking_branch.remote_branch,
                author_name,
                author_email,
                message)
        except abdt_lander.LanderException as e:
            self._clone.call("reset", "--hard")  # fix the working copy
            raise abdt_exception.LandingException(
                str(e),
                self.review_branch_name(),
                self._tracking_branch.base)

        self._clone.push(self._tracking_branch.base)
        self._clone.push_delete(self._tracking_branch.branch)
        self._clone.push_delete(self.review_branch_name())
        # TODO: we probably want to do a better job of cleaning up locally

        self._review_branch = None
        self._tracking_branch = None

        return result

    def _make_git_context(self):
        return abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), branches=None)

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
