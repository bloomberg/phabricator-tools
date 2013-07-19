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
#    .base_branch_name
#    .review_branch_name
#    .tracking_branch_name
#    .review_id_or_none
#    .review_branch
#    .tracking_branch
#    .is_status_bad_pre_review
#    .is_status_bad_land
#    .is_status_bad
#    .has_new_commits
#    .push_delete_tracking_branch
#    .push_bad_land
#    .push_bad_in_review
#    .push_new_bad_in_review
#    .push_bad_pre_review
#    .push_status
#    .push_ok_new_review
#    .get_author_names_emails
#    .get_any_author_emails
#    .make_message_digest
#    .make_raw_diff
#    .verify_review_branch_base
#    .land
#    .get_commit_message_from_tip
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
import abdt_exception
import abdt_gittypes
import abdt_naming
import abdt_workingbranch
import phlgit_log
import phlgitu_ref
import phlsys_fs
import phlsys_subprocess

_MAX_DIFF_SIZE = 1.5 * 1024 * 1024
_DIFF_CONTEXT_LINES = 1000
_LESS_DIFF_CONTEXT_LINES = 100


class ReviewTrackingBranchPair(object):

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
        return not self._clone.is_identical(
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
        hashes = self._get_commit_hashes()
        return phlgit_log.get_author_names_emails_from_hashes(
            self._clone, hashes)

    def get_any_author_emails(self):
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

    def _get_commit_hashes(self):
        hashes = self._clone.get_range_hashes(
            self._review_branch.remote_base,
            self._review_branch.remote_branch)
        return hashes

    def make_message_digest(self):
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
        # TODO: we probably want to do a better job of cleaning up locally

        return result

    def get_commit_message_from_tip(self):
        hashes = self._get_commit_hashes()
        revision = phlgit_log.make_revision_from_hash(self._clone, hashes[-1])
        message = revision.subject + "\n"
        message += "\n"
        message += revision.message + "\n"
        return message


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
