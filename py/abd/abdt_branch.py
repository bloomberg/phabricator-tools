"""Implement operations for branch-based reviews."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_branch
#
# Public Classes:
#   ReviewTrackingBranchPair
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

import abdt_exception
import abdt_gittypes
import abdt_lander
import abdt_naming
import abdt_workingbranch

# TODO: remove direct deps on phl
import phlgit_log
import phlgitu_ref

# TODO: allow these to be passed in
_MAX_DIFF_SIZE = 1.5 * 1024 * 1024
_DIFF_CONTEXT_LINES = 1000
_LESS_DIFF_CONTEXT_LINES = 100


class ReviewTrackingBranchPair(object):

    def __init__(self, clone, review_branch, tracking_branch, lander):
        """Create a new relationship tracker for the supplied branch names.

        :clone: a Git clone to delegate to
        :review_branch: the string name of the author's branch
        :tracking_branch: the string name of Arcyd's branch
        :lander: a lander conformant to abdt_lander

        """
        self._clone = clone
        self._review_branch = review_branch
        self._tracking_branch = tracking_branch
        self._lander = lander

    def is_abandoned(self):
        """Return True if the author's branch no longer exists."""
        return not self._review_branch and self._tracking_branch

    def is_null(self):
        """Return True if we don't have any data."""
        return not self._review_branch and not self._tracking_branch

    def is_new(self):
        """Return True if we haven't marked the author's branch."""
        return self._review_branch and not self._tracking_branch

    def is_status_bad_pre_review(self):
        """Return True if the author's branch is marked 'bad pre-review'."""
        return self._tracking_branch and abdt_naming.isStatusBadPreReview(
            self._tracking_branch)

    def is_status_bad_land(self):
        """Return True if the author's branch is marked 'bad land'."""
        return self._tracking_branch and abdt_naming.isStatusBadLand(
            self._tracking_branch)

    def is_status_bad(self):
        """Return True if the author's branch is marked any bad status."""
        return self._tracking_branch and abdt_naming.isStatusBad(
            self._tracking_branch)

    def has_new_commits(self):
        """Return True if the author's branch is different since marked."""
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
        """Return a list of (name, email) tuples from the branch.

        If the branch has an invalid base or has no history against the base
        then return information from the commit pointed to by the branch.

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

    def _make_raw_diff_helper(self, context=None):
        return self._clone.raw_diff_range(
            self._review_branch.remote_base,
            self._review_branch.remote_branch,
            context)

    def make_raw_diff(self):
        """Return a string raw diff of the changes on the branch.

        If the diff would exceed the _MAX_DIFF_SIZE then take measures
        to reduce the diff size by reducing the amount of context.

        """
        rawDiff = self._make_raw_diff_helper(_DIFF_CONTEXT_LINES)

        if not rawDiff:
            raise abdt_exception.AbdUserException(
                str(
                    "no difference from "
                    + self._review_branch.base
                    + " to "
                    + self._review_branch.branch))

        # if the diff is too big then regen with less context
        if len(rawDiff) >= _MAX_DIFF_SIZE:
            rawDiff = self._make_raw_diff_helper(_LESS_DIFF_CONTEXT_LINES)

        # if the diff is still too big then regen with no context
        if len(rawDiff) >= _MAX_DIFF_SIZE:
            rawDiff = self._make_raw_diff_helper()

        # if the diff is still too big then error
        if len(rawDiff) >= _MAX_DIFF_SIZE:
            raise abdt_exception.LargeDiffException(
                "diff too big", len(rawDiff), _MAX_DIFF_SIZE)

        return rawDiff

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
        # TODO: raise if the branch is not actually abandoned
        self._push_delete_tracking_branch()

    def clear_mark(self):
        """Clear status and last commit associated with the review branch."""
        self._push_delete_tracking_branch()

    def mark_bad_land(self):
        """Mark the current version of the review branch as 'bad land'."""
        context = abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), None)
        abdt_workingbranch.pushBadLand(
            context,
            self._review_branch,
            self._tracking_branch)

    def mark_bad_in_review(self):
        """Mark the current version of the review branch as 'bad in review'."""
        context = abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), None)
        abdt_workingbranch.pushBadInReview(
            context,
            self._review_branch,
            self._tracking_branch)

    def mark_new_bad_in_review(self, review_id):
        """Mark the current version of the review branch as 'bad in review'."""
        context = abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), None)
        wb = abdt_gittypes.makeGitWorkingBranchFromParts(
            abdt_naming.WB_STATUS_BAD_INREVIEW,
            self._review_branch.description,
            self._review_branch.base,
            review_id,
            context.remote)
        self._tracking_branch = wb
        self.mark_bad_in_review()

    def mark_bad_pre_review(self):
        """Mark this version of the review branch as 'bad pre review'."""
        context = abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), None)
        abdt_workingbranch.pushBadPreReview(context, self._review_branch)

    def mark_ok_in_review(self):
        """Mark this version of the review branch as 'ok in review'."""
        status = abdt_naming.WB_STATUS_OK
        context = abdt_gittypes.GitContext(
            self._clone, self._clone.get_remote(), None)
        self._tracking_branch = abdt_workingbranch.pushStatus(
            context,
            self._review_branch,
            self._tracking_branch,
            status)

    def mark_ok_new_review(self, revision_id):
        """Mark this version of the review branch as 'ok in review'."""
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
            phlgitu_ref.make_local(self._tracking_branch.branch))

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

        return result


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
