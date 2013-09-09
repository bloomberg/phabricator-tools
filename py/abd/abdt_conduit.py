"""Abstraction for Arcyd's conduit operations."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_conduit
#
# Public Classes:
#   Conduit
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

from __future__ import absolute_import

import phlcon_differential
import phlcon_user
import phlsys_conduit

import abdt_exception


# TODO: re-order methods as (accessor, mutator)
class Conduit(object):

    def __init__(self, conduit):
        """Initialise a new Conduit.

        :conduit: a phlsys_conduit to delegate to
        :returns: None

        """
        super(Conduit, self).__init__()
        self._conduit = conduit

    def create_comment(self, revision, message, silent=False):
        """Make a comment on the specified 'revision'.

        :revision: id of the revision to comment on
        :message: the string message to leave as a comment, may be empty
        :silent: mail notifications won't be sent if False
        :returns: None

        """
        phlcon_differential.create_comment(
            self._conduit, revision, message, silent=silent)

    def create_empty_revision_as_user(self, username):
        """Return the id of a newly created empty revision as 'username'.

        :username: username for the author of the revision
        :returns: id of created revision

        """
        with phlsys_conduit.act_as_user_context(self._conduit, username):
            revision = phlcon_differential.create_empty_revision(self._conduit)
        return revision

    def get_commit_message(self, revisionid):
        """Return the string commit message appropriate for supplied revision.

        :revisionid: the id of the revision to create a message for
        :returns: the string of the commit message

        """
        return phlcon_differential.get_commit_message(
            self._conduit, revisionid)

    def create_revision_as_user(self, raw_diff, fields, username):
        """Return the id of a newly created revision based on specified args.

        See phlcon_differential.MessageFields for some examples of valid input
        for specified 'fields'.

        :raw_diff: raw output string from e.g. 'git diff master...'
        :fields: dict of string attributes, required: 'title' and 'testPlan'
        :username: username for the author of the revision
        :returns: id of created revision

        """
        with phlsys_conduit.act_as_user_context(self._conduit, username):
            diffid = phlcon_differential.create_raw_diff(
                self._conduit, raw_diff).id
            review = phlcon_differential.create_revision(
                self._conduit, diffid, fields)
        return review.revisionid

    def query_users_from_emails(self, emails):
        """Return a list of username strings based on the provided emails.

        If an email does not correspond to a username then None is inserted in
        its place.

        :emails: a list of strings corresponding to user email addresses
        :returns: a list of strings corresponding to Phabricator usernames

        """
        return phlcon_user.query_users_from_emails(self._conduit, emails)

    def parse_commit_message(self, message):
        """Return a ParseCommitMessageResponse based on 'message'.

        :message: a string message to parse
        :returns: a phlcon_differential.ParseCommitMessageResponse

        """
        message = unicode(message, errors='replace')
        return phlcon_differential.parse_commit_message(self._conduit, message)

    def _get_author_user(self, revisionid):
        # TODO: these queries are very expensive, cache them
        revision = phlcon_differential.query(self._conduit, [revisionid])[0]
        author_user = phlcon_user.query_usernames_from_phids(
            self._conduit, [revision.authorPHID])[0]
        return author_user

    def is_review_accepted(self, revisionid):
        """Return True if the supplied 'revisionid' is in 'accepted' status.

        :revisionid: id of the Differential revision to query
        :returns: True if accepted

        """
        status = phlcon_differential.get_revision_status(
            self._conduit, revisionid)
        return int(status) == phlcon_differential.ReviewStates.accepted

    def update_revision(self, revisionid, raw_diff, message):
        """Update an existing Differential revision with a new diff.

        :revisionid: id of the Differential revision to update
        :raw_diff: raw output string from e.g. 'git diff master...'
        :message: string message to annotate the update event with
        :returns: None

        """
        # do some sanity checks before committing to the expensive operation
        # of storing a diff in Differential
        status = phlcon_differential.get_revision_status(
            self._conduit, revisionid)
        if status == phlcon_differential.ReviewStates.closed:
            raise abdt_exception.AbdUserException(
                "can't update a closed revision")

        author_user = self._get_author_user(revisionid)
        with phlsys_conduit.act_as_user_context(self._conduit, author_user):
            diffid = phlcon_differential.create_raw_diff(
                self._conduit, raw_diff).id
            try:
                phlcon_differential.update_revision(
                    self._conduit, revisionid, diffid, [], message)
            except phlcon_differential.UpdateClosedRevisionError:
                raise abdt_exception.AbdUserException(
                    "CONDUIT: can't update a closed revision")

    def set_requires_revision(self, revisionid):
        """Set an existing Differential revision to 'requires revision'.

        :revisionid: id of the Differential revision to update
        :returns: None

        """
        author_user = self._get_author_user(revisionid)
        with phlsys_conduit.act_as_user_context(self._conduit, author_user):
            phlcon_differential.create_comment(
                self._conduit,
                revisionid,
                action=phlcon_differential.Action.rethink)

    def close_revision(self, revisionid):
        """Set an existing Differential revision to 'closed'.

        :revisionid: id of the Differential revision to close
        :returns: None

        """
        author_user = self._get_author_user(revisionid)
        with phlsys_conduit.act_as_user_context(self._conduit, author_user):
            phlcon_differential.close(self._conduit, revisionid)

    def abandon_revision(self, revisionid):
        """Set an existing Differential revision to 'abandoned'.

        :revisionid: id of the Differential revision to close
        :returns: None

        """
        author_user = self._get_author_user(revisionid)
        with phlsys_conduit.act_as_user_context(self._conduit, author_user):
            phlcon_differential.create_comment(
                self._conduit,
                revisionid,
                action=phlcon_differential.Action.abandon)

    # XXX: test function - will disappear when moved to new processrepo tests
    def accept_revision_as_user(self, revisionid, username):
        """Set an existing Differential revision to 'accepted'.

        :revisionid: id of the Differential revision to accept
        :username: username for the reviewer of the revision
        :returns: None

        """
        with phlsys_conduit.act_as_user_context(self._conduit, username):
            phlcon_differential.create_comment(
                self._conduit,
                revisionid,
                action=phlcon_differential.Action.accept)

    # XXX: test function currently but needed for changing owner in the case
    #      where no valid author is detected on a branch at creation but is
    #      valid later, after the review has been created
    def commandeer_revision_as_user(self, revisionid, username):
        """Change the author of a revision to the specified 'username'.

        :revisionid: id of the Differential revision to claim
        :username: username for the author of the revision
        :returns: None

        """
        with phlsys_conduit.act_as_user_context(self._conduit, username):
            phlcon_differential.create_comment(
                self._conduit,
                revisionid,
                action=phlcon_differential.Action.claim)


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
