"""Abstraction for Arcyd's conduit operations."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_conduit
#
# Public Classes:
#   Conduit
#    .describe
#    .refresh_cache_on_cycle
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

import datetime

import phlcon_differential
import phlcon_reviewstatecache
import phlcon_user
import phlsys_conduit
import phlsys_textconvert

import abdt_exception
import abdt_logging


# TODO: re-order methods as (accessor, mutator)
class Conduit(object):

    def __init__(self, multi_conduit):
        """Initialise a new Conduit.

        :multi_conduit: a phlsys_conduit to delegate to
        :returns: None

        """
        super(Conduit, self).__init__()
        self._multi_conduit = multi_conduit
        self._reviewstate_cache = phlcon_reviewstatecache.ReviewStateCache(
            multi_conduit)

    def describe(self):
        """Return a string description of this conduit for a human to read.

        :returns: a string

        """
        description = None
        if self._multi_conduit.conduit_uri:
            description = self._multi_conduit.conduit_uri
        else:
            description = 'conduit is None'
        return description

    def refresh_cache_on_cycle(self):
        """Refresh the stored state of revisions and users.

        Note that this should be called once per 'cycle' of git
        repositories to avoid degredation of performance.  This is
        necessary because revisions that were not accessed since the
        last refresh are evicted and will not benefit from the batching
        of revision queries.

        """
        self._reviewstate_cache.refresh_active_reviews()

    def create_comment(self, revision, message, silent=False):
        """Make a comment on the specified 'revision'.

        :revision: id of the revision to comment on
        :message: the string message to leave as a comment, may be empty
        :silent: mail notifications won't be sent if False
        :returns: None

        """
        phlcon_differential.create_comment(
            self._multi_conduit, revision, message, silent=silent)
        self._log('conduit-comment', 'commented on {}'.format(revision))

    def create_empty_revision_as_user(self, username):
        """Return the id of a newly created empty revision as 'username'.

        :username: username for the author of the revision
        :returns: id of created revision

        """
        as_user_conduit = self._make_as_user_conduit(username)
        revision = phlcon_differential.create_empty_revision(as_user_conduit)
        self._log(
            'conduit-createemptyrev',
            'created {} as {}'.format(revision, username))
        return revision

    def get_commit_message(self, revisionid):
        """Return the string commit message appropriate for supplied revision.

        :revisionid: the id of the revision to create a message for
        :returns: the string of the commit message

        """
        msg = phlcon_differential.get_commit_message(
            self._multi_conduit, revisionid)
        return phlsys_textconvert.lossy_unicode_to_ascii(msg)

    def create_revision_as_user(self, raw_diff, fields, username):
        """Return the id of a newly created revision based on specified args.

        See phlcon_differential.MessageFields for some examples of valid input
        for specified 'fields'.

        :raw_diff: raw output string from e.g. 'git diff master...'
        :fields: dict of string attributes, required: 'title' and 'testPlan'
        :username: username for the author of the revision
        :returns: id of created revision

        """
        as_user_conduit = self._make_as_user_conduit(username)
        diffid = phlcon_differential.create_raw_diff(
            as_user_conduit, raw_diff).id
        review = phlcon_differential.create_revision(
            as_user_conduit, diffid, fields)
        self._log(
            'conduit-createrev',
            'created {} as {}'.format(review.revisionid, username))
        return review.revisionid

    def query_name_and_phid_from_email(self, email):
        """Return a (username, phid) tuple based on the provided email.

        If an email does not correspond to a user then None is returned.

        :email: a strings of the user's email address
        :returns: a (username, phid) tuple

        """
        user = phlcon_user.query_user_from_email(self._multi_conduit, email)
        result = None
        if user:
            result = (user.userName, user.phid)
        return result

    def query_users_from_emails(self, emails):
        """Return a list of username strings based on the provided emails.

        If an email does not correspond to a username then None is inserted in
        its place.

        :emails: a list of strings corresponding to user email addresses
        :returns: a list of strings corresponding to Phabricator usernames

        """
        return phlcon_user.query_users_from_emails(self._multi_conduit, emails)

    def parse_commit_message(self, message):
        """Return a ParseCommitMessageResponse based on 'message'.

        :message: a string message to parse
        :returns: a phlcon_differential.ParseCommitMessageResponse

        """
        message = phlsys_textconvert.to_unicode(message)
        return phlcon_differential.parse_commit_message(
            self._multi_conduit, message)

    def _get_author_user(self, revisionid):
        # TODO: these queries are very expensive, cache them
        revision = phlcon_differential.query(
            self._multi_conduit, [revisionid])[0]
        author_user = phlcon_user.query_usernames_from_phids(
            self._multi_conduit, [revision.authorPHID])[0]
        return author_user

    def is_review_accepted(self, revisionid):
        """Return True if the supplied 'revisionid' is in 'accepted' status.

        :revisionid: id of the Differential revision to query
        :returns: True if accepted

        """
        state = self._reviewstate_cache.get_state(revisionid)
        return int(state.status) == phlcon_differential.ReviewStates.accepted

    def is_review_abandoned(self, revisionid):
        """Return True if the supplied 'revisionid' is in 'abandoned' status.

        :revisionid: id of the Differential revision to query
        :returns: True if abandoned

        """
        state = self._reviewstate_cache.get_state(revisionid)
        return int(state.status) == phlcon_differential.ReviewStates.abandoned

    def _get_update_age(self, revisionid):
        state = self._reviewstate_cache.get_state(revisionid)
        date_modified = state.date_modified
        update_time = datetime.datetime.fromtimestamp(float(date_modified))
        return datetime.datetime.now() - update_time

    def is_review_recently_updated(self, revisionid):
        """Return True if the supplied 'revisionid' was updated recently.

        'recently' is a subjective term, in the context of a review it seems
        reasonable that if it hasn't been updated for at least a day then it
        could be considered as not recently updated.

        :revisionid: id of the Differential revision to query
        :returns: True if recently updated

        """
        update_age = self._get_update_age(revisionid)
        one_day = datetime.timedelta(days=1)
        return update_age < one_day

    def update_revision(self, revisionid, raw_diff, message):
        """Update an existing Differential revision with a new diff.

        :revisionid: id of the Differential revision to update
        :raw_diff: raw output string from e.g. 'git diff master...'
        :message: string message to annotate the update event with
        :returns: None

        """
        # do some sanity checks before committing to the expensive operation
        # of storing a diff in Differential
        state = self._reviewstate_cache.get_state(revisionid)
        if state.status == phlcon_differential.ReviewStates.closed:
            raise abdt_exception.AbdUserException(
                "can't update a closed revision")

        author_user = self._get_author_user(revisionid)
        as_user_conduit = self._make_as_user_conduit(author_user)
        diffid = phlcon_differential.create_raw_diff(
            as_user_conduit, raw_diff).id
        try:
            phlcon_differential.update_revision(
                as_user_conduit, revisionid, diffid, [], message)
        except phlcon_differential.UpdateClosedRevisionError:
            raise abdt_exception.AbdUserException(
                "CONDUIT: can't update a closed revision")
        self._log(
            'conduit-updaterev',
            'updated {} as {}'.format(revisionid, author_user))

    def set_requires_revision(self, revisionid):
        """Set an existing Differential revision to 'requires revision'.

        :revisionid: id of the Differential revision to update
        :returns: None

        """
        author_user = self._get_author_user(revisionid)
        as_user_conduit = self._make_as_user_conduit(author_user)
        phlcon_differential.create_comment(
            as_user_conduit,
            revisionid,
            action=phlcon_differential.Action.rethink)
        self._log(
            'conduit-setrequiresrev',
            'updated {} as {}'.format(revisionid, author_user))

    def close_revision(self, revisionid):
        """Set an existing Differential revision to 'closed'.

        :revisionid: id of the Differential revision to close
        :returns: None

        """
        author_user = self._get_author_user(revisionid)
        as_user_conduit = self._make_as_user_conduit(author_user)
        phlcon_differential.close(as_user_conduit, revisionid)
        self._log(
            'conduit-close',
            'closed {} as {}'.format(revisionid, author_user))

    def abandon_revision(self, revisionid):
        """Set an existing Differential revision to 'abandoned'.

        :revisionid: id of the Differential revision to close
        :returns: None

        """
        author_user = self._get_author_user(revisionid)
        as_user_conduit = self._make_as_user_conduit(author_user)
        phlcon_differential.create_comment(
            as_user_conduit,
            revisionid,
            action=phlcon_differential.Action.abandon)
        self._log(
            'conduit-abandon',
            'abandoned {} as {}'.format(revisionid, author_user))

    # XXX: test function - will disappear when moved to new processrepo tests
    def accept_revision_as_user(self, revisionid, username):
        """Set an existing Differential revision to 'accepted'.

        :revisionid: id of the Differential revision to accept
        :username: username for the reviewer of the revision
        :returns: None

        """
        as_user_conduit = self._make_as_user_conduit(username)
        phlcon_differential.create_comment(
            as_user_conduit,
            revisionid,
            action=phlcon_differential.Action.accept)
        self._log(
            'conduit-accept',
            'accepted {} as {}'.format(revisionid, username))

    # XXX: test function currently but needed for changing owner in the case
    #      where no valid author is detected on a branch at creation but is
    #      valid later, after the review has been created
    def commandeer_revision_as_user(self, revisionid, username):
        """Change the author of a revision to the specified 'username'.

        :revisionid: id of the Differential revision to claim
        :username: username for the author of the revision
        :returns: None

        """
        as_user_conduit = self._make_as_user_conduit(username)
        phlcon_differential.create_comment(
            as_user_conduit,
            revisionid,
            action=phlcon_differential.Action.claim)
        self._log(
            'conduit-commandeer',
            'commandeered {} as {}'.format(revisionid, username))

    def _log(self, identifier, description):
        abdt_logging.on_io_event(identifier, '{}:{}'.format(
            self.describe(), description))

    def _make_as_user_conduit(self, username):
        return phlsys_conduit.CallMultiConduitAsUser(
            self._multi_conduit, username)


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
