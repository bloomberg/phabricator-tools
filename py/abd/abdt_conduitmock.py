"""Abstraction for Arcyd's conduit operations."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_conduitmock
#
# Public Classes:
#   ConduitMockData
#    .assert_is_user
#    .create_empty_revision_as_user
#    .assert_is_revision
#    .get_revision
#    .is_unchanged
#    .set_changed
#    .set_unchanged
#    .accept_the_only_review
#    .users
#    .revisions
#   ConduitMock
#    .describe
#    .create_comment
#    .create_empty_revision_as_user
#    .get_commit_message
#    .create_revision_as_user
#    .query_name_and_phid_from_email
#    .query_users_from_emails
#    .parse_commit_message
#    .is_review_accepted
#    .is_review_abandoned
#    .is_review_recently_updated
#    .update_revision
#    .set_requires_revision
#    .close_revision
#    .abandon_revision
#    .accept_revision_as_user
#    .commandeer_revision_as_user
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlcon_differential
import phldef_conduit
import phlsys_tracedecorator

import abdt_exception


def _mock_to_str(mock):
    return "conduitmock"


class _RevisionStates(object):
    abandoned = 'abandoned'
    accepted = 'accepted'
    closed = 'closed'
    in_review = 'in-review'
    needs_revision = 'needs-revision'


class _Revision(object):

    def __init__(self, revisionid, author):
        super(_Revision, self).__init__()
        self.revisionid = revisionid
        self.author = author
        self._status = None
        self.set_in_review()

    def set_abandoned(self):
        self._status = _RevisionStates.abandoned

    def set_accepted(self):
        self._status = _RevisionStates.accepted

    def set_closed(self):
        self._status = _RevisionStates.closed

    def set_in_review(self):
        self._status = _RevisionStates.in_review

    def set_needs_revision(self):
        self._status = _RevisionStates.needs_revision

    def is_abandoned(self):
        return self._status == _RevisionStates.abandoned

    def is_accepted(self):
        return self._status == _RevisionStates.accepted

    def is_closed(self):
        return self._status == _RevisionStates.closed


class _User(object):

    def __init__(self, username, email, phid):
        super(_User, self).__init__()
        self.username = username
        self.email = email
        self.phid = phid


class ConduitMockData(object):

    def __init__(self):
        """Initialise a new ConduitMockData."""
        self._revisions = []
        self._users = []
        self._users.append(_User(
            phldef_conduit.ALICE.user,
            phldef_conduit.ALICE.email,
            phldef_conduit.ALICE.phid))
        self._users.append(_User(
            phldef_conduit.BOB.user,
            phldef_conduit.BOB.email,
            phldef_conduit.BOB.phid))
        self._users.append(_User(
            phldef_conduit.PHAB.user,
            phldef_conduit.PHAB.email,
            phldef_conduit.PHAB.phid))
        self._firstid = 101
        self._nextid = self._firstid
        self._no_write_attempts = True

    def assert_is_user(self, username):
        for user in self._users:
            if user.username == username:
                return
        assert False

    def create_empty_revision_as_user(self, username):
        """Return the id of a newly created empty revision as 'username'.

        :username: username for the author of the revision
        :returns: id of created revision

        """
        self.assert_is_user(username)
        revisionid = self._nextid
        self._nextid += 1
        self._revisions.append(_Revision(revisionid, username))
        self.set_changed()
        return revisionid

    def assert_is_revision(self, revisionid):
        revisionid = int(revisionid)
        assert revisionid >= self._firstid
        assert revisionid < self._nextid

    def get_revision(self, revisionid):
        revisionid = int(revisionid)
        self.assert_is_revision(revisionid)
        index = revisionid - self._firstid
        return self._revisions[index]

    def is_unchanged(self):
        """Return true if this conduit has not been written to."""
        return self._no_write_attempts

    def set_changed(self):
        """Reset the unchanged status to the supplied 'value'."""
        self._no_write_attempts = False

    def set_unchanged(self):
        """Reset the unchanged status to the supplied 'value'."""
        self._no_write_attempts = True

    def accept_the_only_review(self):
        """Set the only review as accepted."""
        assert len(self._revisions) == 1
        self._revisions[0].set_accepted()

    @property
    def users(self):
        return self._users

    @property
    def revisions(self):
        return self._revisions


class ConduitMock(object):

    def __init__(self, data=None):
        """Initialise a new ConduitMock."""
        super(ConduitMock, self).__init__()
        self._data = data
        if self._data is None:
            self._data = ConduitMockData()
        phlsys_tracedecorator.decorate_object_methods(self, _mock_to_str)

    def describe(self):
        """Return a string description of this conduit for a human to read.

        :returns: a string

        """
        return 'abdt_conduitmock.ConduitMock'

    def create_comment(self, revision, message, silent=False):
        """Make a comment on the specified 'revision'.

        :revision: id of the revision to comment on
        :message: the string message to leave as a comment, may be empty
        :silent: mail notifications won't be sent if False
        :returns: None

        """
        # unused parameters
        _ = silent  # NOQA

        self._data.assert_is_revision(revision)
        str(message)  # test that message can be converted to string
        self._data.set_changed()

    def create_empty_revision_as_user(self, username):
        """Return the id of a newly created empty revision as 'username'.

        :username: username for the author of the revision
        :returns: id of created revision

        """
        return self._data.create_empty_revision_as_user(username)

    def get_commit_message(self, revisionid):
        """Return the string commit message appropriate for supplied revision.

        :revisionid: the id of the revision to create a message for
        :returns: the string of the commit message

        """
        self._data.assert_is_revision(revisionid)
        return 'DUMMY COMMIT MESSAGE'

    def create_revision_as_user(
            self, raw_diff, fields, username):
        """Return the id of a newly created revision based on specified args.

        See phlcon_differential.MessageFields for some examples of valid input
        for specified 'fields'.

        :raw_diff: raw output string from e.g. 'git diff master...'
        :fields: dict of string attributes, required: 'title' and 'testPlan'
        :username: username for the author of the revision
        :returns: id of created revision

        """
        assert raw_diff
        assert fields
        return self.create_empty_revision_as_user(username)

    def query_name_and_phid_from_email(self, email):
        """Return a (username, phid) tuple based on the provided email.

        If an email does not correspond to a user then None is returned.

        :email: a strings of the user's email address
        :returns: a (username, phid) tuple

        """
        result = None
        for u in self._data.users:
            if u.email == email:
                result = u.username, u.phid
        return result

    def query_users_from_emails(self, emails):
        """Return a list of username strings based on the provided emails.

        If an email does not correspond to a username then None is inserted in
        its place.

        :emails: a list of strings corresponding to user email addresses
        :returns: a list of strings corresponding to Phabricator usernames

        """
        usernames = []
        for e in emails:
            next_username = None
            for u in self._data.users:
                if u.email == e:
                    next_username = u.username
            usernames.append(next_username)
        return usernames

    def parse_commit_message(self, message):
        """Return a ParseCommitMessageResponse based on 'message'.

        :message: a string message to parse
        :returns: a phlcon_differential.ParseCommitMessageResponse

        """
        fields = {'title': 'title', 'testPlan': 'test plan'}
        errors = None
        assert message
        return phlcon_differential.ParseCommitMessageResponse(
            fields=fields, errors=errors)

    def is_review_accepted(self, revisionid):
        """Return True if the supplied 'revisionid' is in 'accepted' status.

        :revisionid: id of the Differential revision to query
        :returns: True if accepted

        """
        revision = self._data.get_revision(revisionid)
        return revision.is_accepted()

    def is_review_abandoned(self, revisionid):
        """Return True if the supplied 'revisionid' is in 'abandoned' status.

        :revisionid: id of the Differential revision to query
        :returns: True if abandoned

        """
        revision = self._data.get_revision(revisionid)
        return revision.is_abandoned()

    def is_review_recently_updated(self, revisionid):
        """Return True if the supplied 'revisionid' was updated recently.

        'recently' is a subjective term, in the context of a review it seems
        reasonable that if it hasn't been updated for at least a day then it
        could be considered as not recently updated.

        :revisionid: id of the Differential revision to query
        :returns: True if recently updated

        """
        return True

    def update_revision(self, revisionid, raw_diff, message):
        """Update an existing Differential revision with a new diff.

        :revisionid: id of the Differential revision to update
        :raw_diff: raw output string from e.g. 'git diff master...'
        :message: string message to annotate the update event with
        :returns: None

        """
        revision = self._data.get_revision(revisionid)

        assert raw_diff
        assert message

        # match the behaviour asserted by phlcon_differential__t,
        # we can't update a closed review, that's an error
        if revision.is_closed():
            raise abdt_exception.AbdUserException(
                "can't update a closed revision")

        # match the behaviour asserted by phlcon_differential__t, 'accepted' is
        # a sticky state as far as updating the review is concerned
        if not revision.is_accepted():
            revision.set_in_review()

        self._data.set_changed()

    def set_requires_revision(self, revisionid):
        """Set an existing Differential revision to 'requires revision'.

        :revisionid: id of the Differential revision to update
        :returns: None

        """
        revision = self._data.get_revision(revisionid)
        assert not revision.is_closed()
        revision.set_needs_revision()
        self._data.set_changed()

    def close_revision(self, revisionid):
        """Set an existing Differential revision to 'closed'.

        :revisionid: id of the Differential revision to close
        :returns: None

        """
        revision = self._data.get_revision(revisionid)
        assert revision.is_accepted()
        revision.set_closed()
        self._data.set_changed()

    def abandon_revision(self, revisionid):
        """Set an existing Differential revision to 'abandoned'.

        :revisionid: id of the Differential revision to close
        :returns: None

        """
        revision = self._data.get_revision(revisionid)
        assert not revision.is_closed()
        revision.set_abandoned()
        self._data.set_changed()

    def accept_revision_as_user(self, revisionid, username):
        """Set an existing Differential revision to 'accepted'.

        :revisionid: id of the Differential revision to accept
        :username: username for the reviewer of the revision
        :returns: None

        """
        revision = self._data.get_revision(revisionid)
        self._data.assert_is_user(username)
        assert not revision.is_closed()
        assert revision.author != username
        revision.set_accepted()
        self._data.set_changed()

    def commandeer_revision_as_user(self, revisionid, username):
        """Change the author of a revision to the specified 'username'.

        :revisionid: id of the Differential revision to claim
        :username: username for the author of the revision
        :returns: None

        """
        revision = self._data.get_revision(revisionid)
        self._data.assert_is_user(username)
        assert not revision.is_closed()
        assert revision.author != username
        revision.author = username
        self._data.set_changed()


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
