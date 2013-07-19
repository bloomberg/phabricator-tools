"""Abstraction for Arcyd's conduit operations."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_conduitmock
#
# Public Classes:
#   ConduitMock
#    .create_comment
#    .create_empty_revision_as_user
#    .get_commit_message
#    .create_revision_as_user
#    .query_users_from_emails
#    .parse_commit_message
#    .is_review_accepted
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

import abdt_conduitabc

import phlcon_differential
import phldef_conduit


class _Revision(object):

    def __init__(self, revisionid, author):
        super(_Revision, self).__init__()
        self.revisionid = revisionid
        self.author = author
        self.status = 'review'


class _User(object):

    def __init__(self, username, email):
        super(_User, self).__init__()
        self.username = username
        self.email = email


class ConduitMock(abdt_conduitabc.ConduitAbc):

    def __init__(self):
        """Initialise a new ConduitMock.

        :returns: None

        """
        super(ConduitMock, self).__init__()
        self._revisions = []
        self._users = []
        self._users.append(_User(
            phldef_conduit.ALICE.user,
            phldef_conduit.ALICE.email))
        self._users.append(_User(
            phldef_conduit.BOB.user,
            phldef_conduit.BOB.email))
        self._users.append(_User(
            phldef_conduit.PHAB.user,
            phldef_conduit.PHAB.email))
        self._firstid = 101
        self._nextid = self._firstid

    def _assert_is_revision(self, revisionid):
        revisionid = int(revisionid)
        assert revisionid >= self._firstid
        assert revisionid < self._nextid

    def _assert_is_user(self, username):
        for user in self._users:
            if user.username == username:
                return
        assert False

    def create_comment(self, revision, message, silent=False):
        """Make a comment on the specified 'revision'.

        :revision: id of the revision to comment on
        :message: the string message to leave as a comment, may be empty
        :silent: mail notifications won't be sent if False
        :returns: None

        """
        # unused parameters
        _ = silent  # NOQA

        self._assert_is_revision(revision)
        str(message)  # test that message can be converted to string

    def create_empty_revision_as_user(self, username):
        """Return the id of a newly created empty revision as 'username'.

        :username: username for the author of the revision
        :returns: id of created revision

        """
        self._assert_is_user(username)
        revisionid = self._nextid
        self._nextid += 1
        self._revisions.append(_Revision(revisionid, username))
        return revisionid

    def get_commit_message(self, revisionid):
        """Return the string commit message appropriate for supplied revision.

        :revisionid: the id of the revision to create a message for
        :returns: the string of the commit message

        """
        self._assert_is_revision(revisionid)
        return 'DUMMY COMMIT MESSAGE'

    def create_revision_as_user(
            self, unused_raw_diff, unused_fields, username):
        """Return the id of a newly created revision based on specified args.

        See phlcon_differential.MessageFields for some examples of valid input
        for specified 'fields'.

        :raw_diff: raw output string from e.g. 'git diff master...'
        :fields: dict of string attributes, required: 'title' and 'testPlan'
        :username: username for the author of the revision
        :returns: id of created revision

        """
        return self.create_empty_revision_as_user(username)

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
            for u in self._users:
                if u.email == e:
                    next_username = u.username
            usernames.append(next_username)
        return usernames

    def parse_commit_message(self, unused_message):
        """Return a ParseCommitMessageResponse based on 'message'.

        :message: a string message to parse
        :returns: a phlcon_differential.ParseCommitMessageResponse

        """
        fields = None
        errors = None
        return phlcon_differential.ParseCommitMessageResponse(
            fields=fields, errors=errors)

    def _get_revision(self, revisionid):
        revisionid = int(revisionid)
        self._assert_is_revision(revisionid)
        index = revisionid - self._firstid
        return self._revisions[index]

    def is_review_accepted(self, revisionid):
        """Return True if the supplied 'revisionid' is in 'accepted' status.

        :revisionid: id of the Differential revision to query
        :returns: True if accepted

        """
        revision = self._get_revision(revisionid)
        return revision.status == 'accepted'

    def update_revision(self, revisionid, unused_raw_diff, unused_message):
        """Update an existing Differential revision with a new diff.

        :revisionid: id of the Differential revision to update
        :raw_diff: raw output string from e.g. 'git diff master...'
        :message: string message to annotate the update event with
        :returns: None

        """
        revision = self._get_revision(revisionid)
        revision.status = 'review'

    def set_requires_revision(self, revisionid):
        """Set an existing Differential revision to 'requires revision'.

        :revisionid: id of the Differential revision to update
        :returns: None

        """
        revision = self._get_revision(revisionid)
        assert revision.status != 'closed'
        revision.status = 'revision'

    def close_revision(self, revisionid):
        """Set an existing Differential revision to 'closed'.

        :revisionid: id of the Differential revision to close
        :returns: None

        """
        revision = self._get_revision(revisionid)
        assert revision.status == 'accepted'
        revision.status = 'revision'

    def abandon_revision(self, revisionid):
        """Set an existing Differential revision to 'abandoned'.

        :revisionid: id of the Differential revision to close
        :returns: None

        """
        revision = self._get_revision(revisionid)
        assert revision.status != 'closed'
        revision.status = 'abandoned'

    def accept_revision_as_user(self, revisionid, username):
        """Set an existing Differential revision to 'closed'.

        :revisionid: id of the Differential revision to close
        :username: username for the reviewer of the revision
        :returns: None

        """
        revision = self._get_revision(revisionid)
        self._assert_is_user(username)
        assert revision.status != 'closed'
        assert revision.author != username
        revision.status = 'accepted'

    def commandeer_revision_as_user(self, revisionid, username):
        """Change the author of a revision to the specified 'username'.

        :revisionid: id of the Differential revision to claim
        :username: username for the author of the revision
        :returns: None

        """
        revision = self._get_revision(revisionid)
        self._assert_is_user(username)
        assert revision.status != 'closed'
        assert revision.author != username
        revision.author = username


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
