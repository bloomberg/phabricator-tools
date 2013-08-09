"""Implement mocked operations for branch-based reviews."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_branchmock
#
# Public Classes:
#   ReviewBranchPairMock
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
# Public Functions:
#   create_simple_new_review
#   logged_call
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import phldef_conduit

import abdt_naming


def create_simple_new_review():
    return ReviewBranchPairMock(
        is_abandoned=False,
        is_null=False,
        is_base_ok=True,
        has_new_commits=True,
        base_branch="base",
        review_branch="review",
        review_id=None,
        names_emails=[(phldef_conduit.ALICE.user, phldef_conduit.ALICE.email)],
        any_emails=None,
        message_digest="digest",
        raw_diff="raw diff",
        branch_tip_message="tip message")


# TODO: we can move this into phl and depend on standard library 'logging'
def logged_call(f):

    def logged_call_imp(self, *args, **kwargs):
        callstring = 'CALL ' + f.__name__ + '('
        for (i, arg) in enumerate(args):
            if i:
                callstring += ', '
            callstring += str(arg)
        callstring += ')'
        self._log(callstring)
        ret = f(self, *args, **kwargs)
        self._log('RETURN ' + str(ret))
        return ret

    return logged_call_imp


class ReviewBranchPairMock(object):

    def __init__(
            self,
            is_abandoned,
            is_null,
            is_base_ok,
            has_new_commits,
            base_branch,
            review_branch,
            review_id,
            names_emails,
            any_emails,
            message_digest,
            raw_diff,
            branch_tip_message):
        """Create a mock relationship tracker.

        :is_abandoned: bool result of self.is_abandoned()
        :is_null: bool result of self.is_null()
        :is_base_ok: bool result of self.verify_review_branch_base()
        :has_new_commits: bool result of self.has_new_commits()
        :base_branch: the string result of self.base_branch_name()
        :review_branch: the string result of self.review_branch_name()
        :review_id: the int result of self.review_id_or_none()
        :names_emails: the list result of self.get_author_names_emails()
        :any_emails: list result of self.get_any_emails() if no names_emails
        :message_digest: the string result of self.make_message_digest()
        :raw_diff: the string result of self.make_raw_diff()
        :branch_tip_message: the result of self.get_commit_message_from_tip()

        """
        self._is_abandoned = is_abandoned
        self._is_null = is_null
        self._is_base_ok = is_base_ok
        self._base_branch = base_branch
        self._review_branch = review_branch
        self._has_new_commits = has_new_commits
        self._review_branch = review_branch
        self._review_id = review_id
        self._names_emails = names_emails
        self._any_emails = any_emails
        self._message_digest = message_digest
        self._raw_diff = raw_diff
        self._branch_tip_message = branch_tip_message
        self._status = None

        assert isinstance(self._review_id, int) or self._review_id is None

    def _log(self, message):
        if self._review_branch is not None:
            print self._review_branch + ':', message
        else:
            print '(NULL branch):', message

    @logged_call
    def is_abandoned(self):
        """Return True if the author's branch no longer exists."""
        return self._is_abandoned

    @logged_call
    def is_null(self):
        """Return True if we don't have any data."""
        return self._is_null

    @logged_call
    def is_new(self):
        """Return True if we haven't marked the author's branch."""
        return self._status is None

    @logged_call
    def is_status_bad_pre_review(self):
        """Return True if the author's branch is marked 'bad pre-review'."""
        return self._status == abdt_naming.WB_STATUS_BAD_PREREVIEW

    @logged_call
    def is_status_bad_land(self):
        """Return True if the author's branch is marked 'bad land'."""
        return self._status == abdt_naming.WB_STATUS_BAD_LAND

    @logged_call
    def is_status_bad(self):
        """Return True if the author's branch is marked any bad status."""
        return self._status.startswith(abdt_naming.WB_STATUS_PREFIX_BAD)

    @logged_call
    def has_new_commits(self):
        """Return True if the author's branch is different since marked."""
        return self._has_new_commits

    @logged_call
    def base_branch_name(self):
        """Return the string name of the branch the review will land on."""
        return self._base_branch

    @logged_call
    def review_branch_name(self):
        """Return the string name of the branch the review is based on."""
        return self._review_branch

    @logged_call
    def review_id_or_none(self):
        """Return the int id of the review or 'None' if there isn't one."""
        return self._review_id

    @logged_call
    def get_author_names_emails(self):
        """Return a list of (name, email) tuples from the branch."""
        return self._names_emails

    @logged_call
    def get_any_author_emails(self):
        """Return a list of email addresses tuples from the branch.

        If the branch has an invalid base or has no history against the base
        then return information from the commit pointed to by the branch.

        Useful if 'get_author_names_emails' fails.

        """
        emails = [i[1] for i in self._names_emails]
        if not emails:
            emails = self._any_emails
        return emails

    @logged_call
    def make_message_digest(self):
        """Return a string digest of the commit messages on the branch.

        The digest is comprised of the title from the earliest commit
        unique to the branch and all of the message bodies from the
        unique commits on the branch.

        """
        return self._message_digest

    @logged_call
    def make_raw_diff(self):
        """Return a string raw diff of the changes on the branch."""
        return self._raw_diff

    @logged_call
    def verify_review_branch_base(self):
        """Raise exception if review branch has invalid base."""
        return self._is_base_ok

    @logged_call
    def get_commit_message_from_tip(self):
        """Return string commit message from latest commit on branch."""
        return self._branch_tip_message

    @logged_call
    def abandon(self):
        """Remove information associated with the abandoned review branch."""
        assert self._is_abandoned
        self._status = None
        self._has_new_commits = False

    @logged_call
    def clear_mark(self):
        """Clear status and last commit associated with the review branch."""
        self._status = None
        self._has_new_commits = True

    @logged_call
    def mark_bad_land(self):
        """Mark the current version of the review branch as 'bad land'."""
        self._status = abdt_naming.WB_STATUS_BAD_LAND
        self._has_new_commits = False

    @logged_call
    def mark_bad_in_review(self):
        """Mark the current version of the review branch as 'bad in review'."""
        # XXX: from the existence of 'mark_new_bad_in_review' it seems like
        #      some checking is required here
        self._status = abdt_naming.WB_STATUS_BAD_INREVIEW
        self._has_new_commits = False

    @logged_call
    def mark_new_bad_in_review(self, review_id):
        """Mark the current version of the review branch as 'bad in review'."""
        # XXX: from the existence of 'mark_bad_in_review' it seems like
        #      some checking is required here
        self._status = abdt_naming.WB_STATUS_BAD_INREVIEW
        self._review_id = int(review_id)
        self._has_new_commits = False

    @logged_call
    def mark_bad_pre_review(self):
        """Mark this version of the review branch as 'bad pre review'."""
        self._status = abdt_naming.WB_STATUS_BAD_PREREVIEW
        self._has_new_commits = False

    @logged_call
    def mark_ok_in_review(self):
        # XXX: from the existence of 'mark_ok_new_review' it seems like
        #      some checking is required here
        """Mark this version of the review branch as 'ok in review'."""
        self._status = abdt_naming.WB_STATUS_OK
        self._has_new_commits = False

    @logged_call
    def mark_ok_new_review(self, review_id):
        # XXX: from the existence of 'mark_ok_in_review' it seems like
        #      some checking is required here
        """Mark this version of the review branch as 'ok in review'."""
        self._status = abdt_naming.WB_STATUS_OK
        self._review_id = int(review_id)
        self._has_new_commits = False

    @logged_call
    def land(self, author_name, author_email, message):
        """Integrate the branch into the base and remove the review branch."""
        self._status = None
        return "landing message"


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
