"""Test suite for abdt_conduit."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] can describe a conduit with non-empty string
# [ B] can query users from emails that are known
# [ B] can query users from invalid emails without error
# [ B] can query users from unknown emails without error
# [  ] raise error if querying users with invalid utf in their email address
# [ C] can parse well-formatted commit message
# [ C] can parse empty commit message
# [ C] can parse commit message with invalid utf
# [ D] can create a revision with 'create_revision_as_user'
# [  ] XXX: commandeeredUpdate
# [  ] XXX: commandeeredLand
# [  ] XXX: createHugeReview
# [  ] XXX: hugeUpdateToReview
# [  ] XXX: processUpdateRepo can handle a review without initial reviewer
# [  ] XXX: landing when dependent review hasn't been landed
# -----------------------------------------------------------------------------
# XXX: make sure we cover each one of these:
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
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_CanQueryUsersFromEmails
# [ C] test_C_CanParseCommitMessage
# [ D] test_D_CanCreateRevisionAsUser
# =============================================================================

from __future__ import absolute_import

import unittest

import phlcon_differential
import phlcon_reviewstatecache
import phldef_conduit
import phlsys_conduit

import abdt_conduit
import abdt_exception


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.test_data = None
        self.sys_conduit = None
        self.reviewstate_cache = None
        self.conduit = None
        self.empty_diff = "diff --git a/ b/"

    def setUp(self):
        self.test_data = phldef_conduit
        self.sys_conduit = phlsys_conduit.MultiConduit(
            self.test_data.TEST_URI,
            self.test_data.PHAB.user,
            self.test_data.PHAB.certificate)
        self.conduit = abdt_conduit.Conduit(
            self.sys_conduit,
            phlcon_reviewstatecache.ReviewStateCache(self.sys_conduit))

    def _invalidate_cache(self):
        self.conduit.refresh_cache_on_cycle()

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        # [ A] can describe a conduit with non-empty string
        self.assertIsInstance(self.conduit.describe(), basestring)
        self.assertGreater(len(self.conduit.describe()), 0)

        # generally exercise all of the conduit methods
        alice = self.test_data.ALICE.user
        bob = self.test_data.BOB.user
        revision = self.conduit.create_empty_revision_as_user(bob)
        self.conduit.create_comment(revision, 'test comment')
        self.conduit.create_comment(
            revision, 'silent test comment', silent=True)
        self.conduit.get_commit_message(revision)
        self.assertFalse(self.conduit.is_review_accepted(revision))
        self.assertFalse(self.conduit.is_review_abandoned(revision))
        self.assertTrue(self.conduit.is_review_recently_updated(revision))
        self.conduit.set_requires_revision(revision)
        self.assertFalse(self.conduit.is_review_accepted(revision))
        self.assertFalse(self.conduit.is_review_abandoned(revision))
        self.assertTrue(self.conduit.is_review_recently_updated(revision))
        self.conduit.accept_revision_as_user(revision, alice)
        self._invalidate_cache()
        self.assertTrue(self.conduit.is_review_accepted(revision))
        self.assertFalse(self.conduit.is_review_abandoned(revision))
        self.assertTrue(self.conduit.is_review_recently_updated(revision))
        self.conduit.set_requires_revision(revision)
        self._invalidate_cache()
        self.assertFalse(self.conduit.is_review_accepted(revision))
        self.assertFalse(self.conduit.is_review_abandoned(revision))
        self.assertTrue(self.conduit.is_review_recently_updated(revision))
        self.conduit.accept_revision_as_user(revision, alice)

        # check that the review is still accepted after an update
        self._invalidate_cache()
        self.assertTrue(self.conduit.is_review_accepted(revision))
        self.assertFalse(self.conduit.is_review_abandoned(revision))
        self.assertTrue(self.conduit.is_review_recently_updated(revision))
        self.conduit.update_revision(revision, self.empty_diff, 'update')
        self._invalidate_cache()
        self.assertTrue(self.conduit.is_review_accepted(revision))
        self.assertFalse(self.conduit.is_review_abandoned(revision))
        self.assertTrue(self.conduit.is_review_recently_updated(revision))

        self.conduit.abandon_revision(revision)
        self.conduit.get_commit_message(revision)

        self._invalidate_cache()
        self.assertFalse(self.conduit.is_review_accepted(revision))
        self.assertTrue(self.conduit.is_review_abandoned(revision))
        self.assertTrue(self.conduit.is_review_recently_updated(revision))

        # un-abandon
        as_user_conduit = phlsys_conduit.CallMultiConduitAsUser(
            self.sys_conduit, bob)
        phlcon_differential.create_comment(
            as_user_conduit,
            revision,
            action=phlcon_differential.Action.reclaim)

        self._invalidate_cache()
        self.assertFalse(self.conduit.is_review_accepted(revision))
        self.assertFalse(self.conduit.is_review_abandoned(revision))
        self.assertTrue(self.conduit.is_review_recently_updated(revision))

        self.conduit.commandeer_revision_as_user(revision, alice)
        self.conduit.commandeer_revision_as_user(revision, bob)

        # close non-accepted revision
        # self.conduit.set_requires_revision(revision)
        # self.assertFalse(self.conduit.is_review_accepted(revision))
        # self.conduit.close_revision(revision)
        # self.assertFalse(self.conduit.is_review_accepted(revision))

        # close revision
        self.conduit.accept_revision_as_user(revision, alice)
        self._invalidate_cache()
        self.assertTrue(self.conduit.is_review_accepted(revision))
        self.assertFalse(self.conduit.is_review_abandoned(revision))
        self.assertTrue(self.conduit.is_review_recently_updated(revision))
        self.conduit.close_revision(revision)
        self.conduit.get_commit_message(revision)

        # commandeer closed revision
        # self.conduit.commandeer_revision_as_user(revision, alice)

        # update closed revision
        self._invalidate_cache()
        self.assertRaises(
            abdt_exception.AbdUserException,
            self.conduit.update_revision,
            revision,
            self.empty_diff,
            'update')

        # comment on closed revision
        self.conduit.create_comment(revision, 'test comment')

        # set closed revision requires revision
        # self.conduit.set_requires_revision(revision)

        # abandon closed revision
        # self.conduit.abandon_revision(revision)

        # try to change author whilst upd/closing/abandoning/commandeering etc.

        # create revision
        # query users
        # parse_commit_message

    def test_B_CanQueryUsersFromEmails(self):
        data = {
            self.test_data.PHAB.email: self.test_data.PHAB.user,
            self.test_data.ALICE.email: self.test_data.ALICE.user,
            self.test_data.BOB.email: self.test_data.BOB.user,
            'a@b.com': None,
            '': None,
            'a': None,
            '/////////': None,
            # '\x80': None, # TODO: we should handle this
        }
        valid_emails = [email for email in data if data[email] is not None]
        valid_users = [data[email] for email in valid_emails]
        invalid_emails = [email for email in data if data[email] is None]
        all_emails = data.keys()
        all_users = [data[email] for email in all_emails]

        # test all valid emails
        self.assertListEqual(
            self.conduit.query_users_from_emails(valid_emails), valid_users)

        # test all invalid emails
        self.assertListEqual(
            self.conduit.query_users_from_emails(invalid_emails),
            [None] * len(invalid_emails))

        # test all emails
        self.assertListEqual(
            self.conduit.query_users_from_emails(all_emails), all_users)

        # test no emails
        self.assertListEqual(self.conduit.query_users_from_emails([]), [])

        # test individual emails
        for (email, user) in data.iteritems():
            self.assertListEqual(
                self.conduit.query_users_from_emails([email]), [user])

    def test_C_CanParseCommitMessage(self):

        # empty message
        self.conduit.parse_commit_message('')

        # well-formed message
        title = 'Title'
        summary = 'This is my description.'
        test_plan = 'This is my test plan.'
        commit_message = '\n'.join([
            title, '\n', summary, 'Test Plan: ' + test_plan])
        result = self.conduit.parse_commit_message(commit_message)
        self.assertSequenceEqual(
            result.fields[phlcon_differential.MessageFields.title], title)
        self.assertSequenceEqual(
            result.fields[phlcon_differential.MessageFields.summary], summary)
        self.assertEqual(
            result.fields[phlcon_differential.MessageFields.test_plan],
            test_plan)

        # bad-utf message
        result = self.conduit.parse_commit_message('\x80' + title)
        self.assertIn(
            title,
            result.fields[phlcon_differential.MessageFields.title])
        self.assertNotEqual(
            title,
            result.fields[phlcon_differential.MessageFields.title])

    def test_D_CanCreateRevisionAsUser(self):
        revision = self.conduit.create_revision_as_user(
            self.empty_diff,
            {'title': 'test_D_CanCreateRevisionAsUser', 'testPlan': 'NONE'},
            self.test_data.ALICE.user)

        self.assertFalse(self.conduit.is_review_accepted(revision))


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
