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
#    .is_status_bad_abandoned
#    .is_status_bad
#    .has_new_commits
#    .base_branch_name
#    .review_branch_hash
#    .review_branch_name
#    .review_id_or_none
#    .get_author_names_emails
#    .get_any_author_emails
#    .get_repo_name
#    .get_browse_url
#    .describe
#    .describe_new_commits
#    .make_message_digest
#    .make_raw_diff
#    .verify_review_branch_base
#    .get_commit_message_from_tip
#    .abandon
#    .remove
#    .clear_mark
#    .mark_bad_land
#    .mark_bad_abandoned
#    .mark_bad_in_review
#    .mark_new_bad_in_review
#    .mark_bad_pre_review
#    .mark_ok_in_review
#    .mark_ok_new_review
#    .land
#
# Public Functions:
#   calc_is_ok
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
# TODO: write test driver

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import phlgit_log
import phlgit_push
import phlgit_revparse
import phlgitu_ref
import phlsys_textconvert

import abdt_differ
import abdt_errident
import abdt_exception
import abdt_lander
import abdt_naming
import abdt_tryloop

# TODO: allow this to be passed in
_MAX_DIFF_SIZE = int(1.5 * 1024 * 1024)


def calc_is_ok(branch):
    """Return True if the supplied 'branch' is ok, False if bad, else None.

    Note that a branch can be 'null' in which case we return None.

    :branch: the Branch to examine
    :returns: bool status of the branch

    """
    assert branch is not None
    if branch.is_null() or branch.is_new() or branch.is_abandoned():
        return None

    return not branch.is_status_bad()


class Branch(object):

    def __init__(
            self,
            repo,
            review_branch,
            review_hash,
            tracking_branch,
            tracking_hash,
            lander,
            repo_name,
            browse_url=None):
        """Create a new relationship tracker for the supplied branch names.

        :repo: a callable supporting git commands, e.g. repo("status")
        :review_branch: the abdt_gittypes.GitReviewBranch
        :review_hash: the commit hash of the branch or None
        :tracking_branch: the abdt_gittypes.GitWorkingBranch
        :tracking_hash: the commit hash of the branch or None
        :lander: a lander conformant to abdt_lander
        :repo_name: a short string to identify the repo to humans
        :browse_url: a URL to browse the branch or repo (may be None)

        """
        self._repo = repo
        self._review_branch = review_branch
        self._review_hash = review_hash
        self._tracking_branch = tracking_branch
        self._tracking_hash = tracking_hash
        self._lander = lander
        assert self._review_branch_valid_or_none()
        assert self._tracking_branch_valid_or_none()
        self._repo_name = repo_name
        self._browse_url = browse_url
        assert self._repo_name is not None

    def _review_branch_valid_or_none(self):
        if not self._has_review_branch():
            return True
        else:
            return isinstance(
                self._review_branch,
                abdt_naming.ReviewBranch)

    def _tracking_branch_valid_or_none(self):
        if not self._has_tracking_branch():
            return True
        else:
            return isinstance(
                self._tracking_branch,
                abdt_naming.TrackerBranch)

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

    def is_status_bad_abandoned(self):
        """Return True if the author's branch is marked 'bad abandoned'."""
        if self._has_tracking_branch():
            branch = self._tracking_branch
            return branch.status == abdt_naming.WB_STATUS_BAD_ABANDONED
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
            return self._review_hash != self._tracking_hash

    def base_branch_name(self):
        """Return the string name of the branch the review will land on."""
        if self._review_branch:
            return self._review_branch.base
        return self._tracking_branch.base

    def review_branch_hash(self):
        """Return the string hash of the review branch or None."""
        return self._review_hash

    def review_branch_name(self):
        """Return the string name of the branch the review is based on."""
        if self._review_branch:
            return self._review_branch.branch
        return self._tracking_branch.review_name

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

        # names and emails are only mentioned once, in the order that they
        # appear.  reverse the order so that the the most recent commit is
        # considered first.
        hashes.reverse()
        names_emails = phlgit_log.get_author_names_emails_from_hashes(
            self._repo, hashes)
        names_emails.reverse()

        return names_emails

    def get_any_author_emails(self):
        """Return a list of emails from the branch.

        If the branch has an invalid base or has no history against the base
        then resort to using the whole history.

        Useful if 'get_author_names_emails' fails.

        """
        if phlgit_revparse.get_sha1_or_none(
                self._repo, self._review_branch.remote_base) is None:
            hashes = phlgit_log.get_last_n_commit_hashes_from_ref(
                self._repo, 1, self._review_branch.remote_branch)
        else:
            hashes = self._get_commit_hashes()
        if not hashes:
            hashes = phlgit_log.get_last_n_commit_hashes_from_ref(
                self._repo, 1, self._review_branch.remote_branch)
        committers = phlgit_log.get_author_names_emails_from_hashes(
            self._repo, hashes)
        emails = [committer[1] for committer in committers]
        return emails

    def get_repo_name(self):
        """Return the human name for the repo the branch came from."""
        return self._repo_name

    def get_browse_url(self):
        """Return the url to browse this branch, may be None."""
        return self._browse_url

    def _get_commit_hashes(self):
        hashes = self._repo.get_range_hashes(
            self._review_branch.remote_base,
            self._review_branch.remote_branch)
        return hashes

    def describe(self):
        """Return a string description of this branch for a human to read."""
        branch_description = "(null branch)"
        if not self.is_null():
            branch_description = self.review_branch_name()
            if self.is_abandoned():
                branch_description += " (abandoned)"
        return "{}, {}".format(self.get_repo_name(), branch_description)

    def describe_new_commits(self, max_commits=100, max_size=16000):
        """Return a string description of the new commits on the branch."""
        hashes = None
        previous = None
        latest = self._review_branch.remote_branch

        if self.is_new():
            previous = self._review_branch.remote_base
        else:
            previous = self._tracking_branch.remote_branch

        hashes = self._repo.get_range_hashes(previous, latest)
        hashes.reverse()
        revisions = self._repo.make_revisions_from_hashes(hashes)

        message = ""
        count = 0
        message_size = 0
        for r in revisions:
            new_message = r.abbrev_hash + " " + r.subject + "\n"
            count += 1
            message_size += len(new_message)
            if count > max_commits or message_size > max_size:
                message += "...{num_commits} commits not shown.\n".format(
                    num_commits=len(revisions) - count + 1)
                break
            else:
                message += new_message
        return phlsys_textconvert.ensure_ascii(message)

    def make_message_digest(self):
        """Return a string digest of the commit messages on the branch.

        The digest is comprised of the title from the earliest commit
        unique to the branch and all of the message bodies from the
        unique commits on the branch.

        """
        hashes = self._get_commit_hashes()
        revisions = self._repo.make_revisions_from_hashes(hashes)
        message = revisions[0].subject + "\n\n"
        for r in revisions:
            message += r.message
        return phlsys_textconvert.ensure_ascii(message)

    def make_raw_diff(self):
        """Return an abdt_differ.DiffResult of the changes on the branch.

        If the diff would exceed the pre-specified max diff size then take
        measures to reduce the diff.

        """
        try:
            return self._repo.checkout_make_raw_diff(
                self._review_branch.remote_base,
                self._review_branch.remote_branch,
                _MAX_DIFF_SIZE)
        except abdt_differ.NoDiffError:
            raise abdt_exception.NoDiffException(
                self.base_branch_name(),
                self.review_branch_name(),
                self.review_branch_hash())

    def _is_based_on(self, name, base):
        # TODO: actually do this
        return True

    def verify_review_branch_base(self):
        """Raise exception if review branch has invalid base."""
        if self._review_branch.base not in self._repo.get_remote_branches():
            raise abdt_exception.MissingBaseException(
                self._review_branch.branch,
                self._review_branch.description,
                self._review_branch.base)
        if not self._is_based_on(
                self._review_branch.branch, self._review_branch.base):
            raise abdt_exception.AbdUserException(
                "'" + self._review_branch.branch +
                "' is not based on '" + self._review_branch.base + "'")

    def get_commit_message_from_tip(self):
        """Return string commit message from latest commit on branch."""
        hashes = self._get_commit_hashes()
        revision = phlgit_log.make_revision_from_hash(self._repo, hashes[-1])
        message = revision.subject + "\n"
        message += "\n"
        message += revision.message + "\n"
        return phlsys_textconvert.ensure_ascii(message)

    def _push_delete_review_branch(self):
        def action():
            self._repo.push_delete(self._review_branch.branch)

        self._tryloop(action, abdt_errident.PUSH_DELETE_REVIEW)

    def _push_delete_tracking_branch(self):
        def action():
            self._repo.push_delete(self._tracking_branch.branch)

        self._tryloop(action, abdt_errident.PUSH_DELETE_TRACKING)

    def abandon(self):
        """Remove information associated with the abandoned review branch."""
        # TODO: raise if the branch is not actually abandoned by the user
        self._push_delete_tracking_branch()
        self._tracking_branch = None
        self._tracking_hash = None

    def remove(self):
        """Remove review branch and tracking branch."""
        self._repo.archive_to_abandoned(
            self._review_hash,
            self.review_branch_name(),
            self._tracking_branch.base)

        # push the abandoned archive, don't escalate if it fails to push
        try:
            # XXX: oddly pylint complains if we call push_landed() directly:
            #      "Using method (_tryloop) as an attribute (not invoked)"
            def push_abandoned():
                self._repo.push_abandoned()

            self._tryloop(
                push_abandoned,
                abdt_errident.PUSH_ABANDONED_ARCHIVE)
        except Exception:
            # XXX: don't worry if we can't push the landed, this is most
            #      likely a permissioning issue but not a showstopper.
            #      we should probably nag on the review instead.
            pass

        self._push_delete_review_branch()
        self._push_delete_tracking_branch()
        self._review_branch = None
        self._review_hash = None
        self._tracking_branch = None
        self._tracking_hash = None

    def clear_mark(self):
        """Clear status and last commit associated with the review branch."""
        self._push_delete_tracking_branch()
        self._tracking_branch = None
        self._tracking_hash = None

    def mark_bad_land(self):
        """Mark the current version of the review branch as 'bad land'."""
        assert self.review_id_or_none() is not None

        self._tryloop(
            lambda: self._push_status(abdt_naming.WB_STATUS_BAD_LAND),
            abdt_errident.MARK_BAD_LAND)

    def mark_bad_abandoned(self):
        """Mark the current version of the review branch as 'bad abandoned'."""
        assert self.review_id_or_none() is not None

        self._tryloop(
            lambda: self._push_status(abdt_naming.WB_STATUS_BAD_ABANDONED),
            abdt_errident.MARK_BAD_ABANDONED)

    def mark_bad_in_review(self):
        """Mark the current version of the review branch as 'bad in review'."""
        assert self.review_id_or_none() is not None

        self._tryloop(
            lambda: self._push_status(abdt_naming.WB_STATUS_BAD_INREVIEW),
            abdt_errident.MARK_BAD_IN_REVIEW)

    def mark_new_bad_in_review(self, revision_id):
        """Mark the current version of the review branch as 'bad in review'."""
        assert self.review_id_or_none() is None

        def action():
            if not self.is_new():
                # 'push_bad_new_in_review' wont clean up our existing tracker
                self._push_delete_tracking_branch()
            self._push_new(
                abdt_naming.WB_STATUS_BAD_INREVIEW,
                revision_id)

        self._tryloop(action, abdt_errident.MARK_NEW_BAD_IN_REVIEW)

    def mark_bad_pre_review(self):
        """Mark this version of the review branch as 'bad pre review'."""
        assert self.review_id_or_none() is None
        assert self.is_status_bad_pre_review() or self.is_new()

        # early out if this operation is redundant, pushing is expensive
        if self.is_status_bad_pre_review() and not self.has_new_commits():
            return

        def action():
            self._push_new(
                abdt_naming.WB_STATUS_BAD_PREREVIEW,
                None)

        self._tryloop(
            action, abdt_errident.MARK_BAD_PRE_REVIEW)

    def mark_ok_in_review(self):
        """Mark this version of the review branch as 'ok in review'."""
        assert self.review_id_or_none() is not None

        self._tryloop(
            lambda: self._push_status(abdt_naming.WB_STATUS_OK),
            abdt_errident.MARK_OK_IN_REVIEW)

    def mark_ok_new_review(self, revision_id):
        """Mark this version of the review branch as 'ok in review'."""
        assert self.review_id_or_none() is None

        def action():
            if not self.is_new():
                # 'push_bad_new_in_review' wont clean up our existing tracker
                self._push_delete_tracking_branch()
            self._push_new(
                abdt_naming.WB_STATUS_OK,
                revision_id)

        self._tryloop(action, abdt_errident.MARK_OK_NEW_REVIEW)

    def land(self, author_name, author_email, message):
        """Integrate the branch into the base and remove the review branch."""

        self._repo.checkout_forced_new_branch(
            self._tracking_branch.base,
            self._tracking_branch.remote_base)

        try:
            result = self._lander(
                self._repo,
                self._tracking_branch.remote_branch,
                author_name,
                author_email,
                message)
        except abdt_lander.LanderException as e:
            self._repo("reset", "--hard")  # fix the working copy
            raise abdt_exception.LandingException(
                str(e),
                self.review_branch_name(),
                self._tracking_branch.base)

        landing_hash = phlgit_revparse.get_sha1(
            self._repo, self._tracking_branch.base)

        # don't tryloop here as it's more expected that we can't push the base
        # due to permissioning or some other error
        try:
            self._repo.push(self._tracking_branch.base)
        except Exception as e:
            raise abdt_exception.LandingPushBaseException(
                str(e),
                self.review_branch_name(),
                self._tracking_branch.base)

        self._tryloop(
            lambda: self._repo.push_delete(
                self._tracking_branch.branch,
                self.review_branch_name()),
            abdt_errident.PUSH_DELETE_LANDED)

        self._repo.archive_to_landed(
            self._tracking_hash,
            self.review_branch_name(),
            self._tracking_branch.base,
            landing_hash,
            message)

        # push the landing archive, don't escalate if it fails to push
        try:
            # XXX: oddly pylint complains if we call push_landed() directly:
            #      "Using method (_tryloop) as an attribute (not invoked)"
            def push_landed():
                self._repo.push_landed()

            self._tryloop(
                push_landed,
                abdt_errident.PUSH_LANDING_ARCHIVE)
        except Exception:
            # XXX: don't worry if we can't push the landed, this is most
            #      likely a permissioning issue but not a showstopper.
            #      we should probably nag on the review instead.
            pass

        self._review_branch = None
        self._review_hash = None
        self._tracking_branch = None
        self._tracking_hash = None

        return result

    def _push_status(self, status):
        old_branch = self._tracking_branch.branch

        self._tracking_branch.update_status(status)

        new_branch = self._tracking_branch.branch
        if old_branch == new_branch:
            phlgit_push.push_asymmetrical_force(
                self._repo,
                self._review_branch.remote_branch,
                phlgitu_ref.make_local(new_branch),
                self._tracking_branch.remote)
        else:
            phlgit_push.move_asymmetrical(
                self._repo,
                self._review_branch.remote_branch,
                phlgitu_ref.make_local(old_branch),
                phlgitu_ref.make_local(new_branch),
                self._repo.get_remote())

        self._tracking_hash = self._review_hash

    def _push_new(self, status, revision_id):
        tracking_branch = self._review_branch.make_tracker(
            status, revision_id)

        phlgit_push.push_asymmetrical_force(
            self._repo,
            self._review_branch.remote_branch,
            phlgitu_ref.make_local(tracking_branch.branch),
            tracking_branch.remote)

        self._tracking_branch = tracking_branch
        self._tracking_hash = self._review_hash

    def _tryloop(self, f, identifier):
        return abdt_tryloop.tryloop(f, identifier, self.describe())


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
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
