"""Implement mocked operations for branch-based reviews."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_branchmock
#
# Public Classes:
#   BranchMockData
#   BranchMock
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
#    .get_repo_name
#    .get_browse_url
#    .get_clone
#    .describe
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
#   create_ok_names_emails
#   create_bad_names_emails
#   create_simple_new_review
#   create_new_review_invalid_base
#   create_review_no_initial_author
#   create_review_no_commits
#   create_review_removed
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phldef_conduit
import phlsys_tracedecorator

import abdt_exception
import abdt_naming


def create_ok_names_emails():
    return [(phldef_conduit.ALICE.user, phldef_conduit.ALICE.email)]


def create_bad_names_emails():
    return [(phldef_conduit.NOTAUSER.user, phldef_conduit.NOTAUSER.email)]


def create_simple_new_review(repo_name='name', branch_url=None):
    data = BranchMockData(
        is_abandoned=False,
        is_null=False,
        is_base_ok=True,
        has_new_commits=True,
        base_branch="base",
        review_branch="review",
        revision_id=None,
        names_emails=[(phldef_conduit.ALICE.user, phldef_conduit.ALICE.email)],
        any_emails=None,
        message_digest="digest",
        raw_diff="raw diff",
        branch_tip_message="tip message",
        repo_name=repo_name,
        branch_url=branch_url)

    return BranchMock(data), data


def create_new_review_invalid_base():
    mock, data = create_simple_new_review()
    data.is_base_ok = False
    return mock, data


def create_review_no_initial_author():
    mock, data = create_simple_new_review()
    data.names_emails = create_bad_names_emails()
    data.any_emails = [phldef_conduit.ALICE.email]
    return mock, data


def create_review_no_commits():
    mock, data = create_simple_new_review()
    data.message_digest = ""
    data.names_emails = []
    data.raw_diff = ""
    data.branch_tip_message = None
    data.any_emails = [phldef_conduit.ALICE.email]
    return mock, data


def create_review_removed():
    mock, data = create_simple_new_review()
    data.is_abandoned = True
    return mock, data


def _mock_to_str(mock):
    if mock._data.review_branch is not None:
        return "BranchMock(" + mock._data.review_branch + ")"
    else:
        return '(NULL branch)'


class BranchMockData(object):

    def __init__(
            self,
            is_abandoned,
            is_null,
            is_base_ok,
            has_new_commits,
            base_branch,
            review_branch,
            revision_id,
            names_emails,
            any_emails,
            message_digest,
            raw_diff,
            branch_tip_message,
            repo_name,
            branch_url):
        """Create data for a mock relationship tracker.

        :is_abandoned: bool result of self.is_abandoned()
        :is_null: bool result of self.is_null()
        :is_base_ok: bool result of self.verify_review_branch_base()
        :has_new_commits: bool result of self.has_new_commits()
        :base_branch: the string result of self.base_branch_name()
        :review_branch: the string result of self.review_branch_name()
        :revision_id: the int result of self.review_id_or_none()
        :names_emails: the list result of self.get_author_names_emails()
        :any_emails: list result of self.get_any_emails() if no names_emails
        :message_digest: the string result of self.make_message_digest()
        :raw_diff: the string result of self.make_raw_diff()
        :branch_tip_message: the result of self.get_commit_message_from_tip()
        :repo_name: the name of the repository, returned by get_repo_name()
        :branch_url: the url to browse the url, returned by get_browse_url()

        """
        super(BranchMockData, self).__init__()
        self.is_abandoned = is_abandoned
        self.is_null = is_null
        self.is_base_ok = is_base_ok
        self.base_branch = base_branch
        self.review_branch = review_branch
        self.has_new_commits = has_new_commits
        self.review_branch = review_branch
        self.revision_id = revision_id
        self.names_emails = names_emails
        self.any_emails = any_emails
        self.message_digest = message_digest
        self.raw_diff = raw_diff
        self.branch_tip_message = branch_tip_message
        self.status = None
        self.repo_name = repo_name
        self.branch_url = branch_url

        assert isinstance(self.revision_id, int) or self.revision_id is None


class BranchMock(object):

    def __init__(self, data):
        """Create a mock relationship tracker.

        :data: BranchMockData object for this mock to use

        """
        super(BranchMock, self).__init__()
        self._data = data
        phlsys_tracedecorator.decorate_object_methods(self, _mock_to_str)

    def _log(self, message):
        if self._data.review_branch is not None:
            print self._data.review_branch + ':', message
        else:
            print '(NULL branch):', message

    def is_abandoned(self):
        """Return True if the author's branch no longer exists."""
        return self._data.is_abandoned

    def is_null(self):
        """Return True if we don't have any data."""
        return self._data.is_null

    def is_new(self):
        """Return True if we haven't marked the author's branch."""
        return self._data.status is None

    def is_status_bad_pre_review(self):
        """Return True if the author's branch is marked 'bad pre-review'."""
        return self._data.status == abdt_naming.WB_STATUS_BAD_PREREVIEW

    def is_status_bad_land(self):
        """Return True if the author's branch is marked 'bad land'."""
        return self._data.status == abdt_naming.WB_STATUS_BAD_LAND

    def is_status_bad(self):
        """Return True if the author's branch is marked any bad status."""
        if self._data.status:
            return self._data.status.startswith(
                abdt_naming.WB_STATUS_PREFIX_BAD)
        return False

    def has_new_commits(self):
        """Return True if the author's branch is different since marked."""
        return self._data.has_new_commits

    def base_branch_name(self):
        """Return the string name of the branch the review will land on."""
        return self._data.base_branch

    def review_branch_name(self):
        """Return the string name of the branch the review is based on."""
        return self._data.review_branch

    def review_id_or_none(self):
        """Return the int id of the review or 'None' if there isn't one."""
        return self._data.revision_id

    def get_author_names_emails(self):
        """Return a list of (name, email) tuples from the branch."""
        return self._data.names_emails

    def get_any_author_emails(self):
        """Return a list of emails from the branch.

        If the branch has an invalid base or has no history against the base
        then resort to using the whole history.

        Useful if 'get_author_names_emails' fails.

        """
        emails = [i[1] for i in self._data.names_emails]
        if not emails:
            emails = self._data.any_emails
        return emails

    def get_repo_name(self):
        """Return the human name for the repo the branch came from."""
        return self._data.repo_name

    def get_browse_url(self):
        """Return the url to browse this branch, may be None."""
        return self._data.branch_url

    def get_clone(self):
        """Return the abdt_clone for this branch."""
        assert False

    def describe(self):
        """Return a string description of this branch for a human to read."""
        return "description!"

    def make_message_digest(self):
        """Return a string digest of the commit messages on the branch.

        The digest is comprised of the title from the earliest commit
        unique to the branch and all of the message bodies from the
        unique commits on the branch.

        """
        return self._data.message_digest

    def make_raw_diff(self):
        """Return a string raw diff of the changes on the branch.

        If the diff would exceed the pre-specified max diff size then take
        measures to reduce the diff.

        """
        return self._data.raw_diff

    def verify_review_branch_base(self):
        """Raise exception if review branch has invalid base."""
        if not self._data.is_base_ok:
            raise abdt_exception.MissingBaseException(
                self._data.review_branch,
                'description',
                self._data.base_branch)

        # TODO: also test raising AbdUserException
        # if not self._is_based_on(
        #         self._review_branch.branch, self._review_branch.base):
        #     raise abdt_exception.AbdUserException(
        #         "'" + self._review_branch.branch +
        #         "' is not based on '" + self._review_branch.base + "'")

    def get_commit_message_from_tip(self):
        """Return string commit message from latest commit on branch."""
        if self._data.branch_tip_message is None:
            raise Exception('branch tip message is None')
        return self._data.branch_tip_message

    def abandon(self):
        """Remove information associated with the abandoned review branch."""
        assert self._data.is_abandoned
        self._data.status = None
        self._data.has_new_commits = False
        self._data.is_null = True
        self._data.revision_id = None

    def clear_mark(self):
        """Clear status and last commit associated with the review branch."""
        self._data.status = None
        self._data.has_new_commits = True
        self._data.revision_id = None

    def mark_bad_land(self):
        """Mark the current version of the review branch as 'bad land'."""
        assert self.review_id_or_none() is not None
        self._data.status = abdt_naming.WB_STATUS_BAD_LAND
        self._data.has_new_commits = False

    def mark_bad_in_review(self):
        """Mark the current version of the review branch as 'bad in review'."""
        assert self.review_id_or_none() is not None
        self._data.status = abdt_naming.WB_STATUS_BAD_INREVIEW
        self._data.has_new_commits = False

    def mark_new_bad_in_review(self, revision_id):
        """Mark the current version of the review branch as 'bad in review'."""
        assert self.review_id_or_none() is None
        self._data.status = abdt_naming.WB_STATUS_BAD_INREVIEW
        self._data.revision_id = int(revision_id)
        self._data.has_new_commits = False

    def mark_bad_pre_review(self):
        """Mark this version of the review branch as 'bad pre review'."""
        assert self.review_id_or_none() is None
        assert self.is_status_bad_pre_review() or self.is_new()
        self._data.status = abdt_naming.WB_STATUS_BAD_PREREVIEW
        self._data.has_new_commits = False
        self._data.revision_id = None

    def mark_ok_in_review(self):
        """Mark this version of the review branch as 'ok in review'."""
        assert self.review_id_or_none() is not None
        self._data.status = abdt_naming.WB_STATUS_OK
        self._data.has_new_commits = False

    def mark_ok_new_review(self, revision_id):
        """Mark this version of the review branch as 'ok in review'."""
        assert self.review_id_or_none() is None
        self._data.status = abdt_naming.WB_STATUS_OK
        self._data.revision_id = int(revision_id)
        self._data.has_new_commits = False

    def land(self, author_name, author_email, message):
        """Integrate the branch into the base and remove the review branch."""
        self._data.status = None
        self._data.is_null = True
        return "\n".join([
            "landing message:", author_name, author_email, message])


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
