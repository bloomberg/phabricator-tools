"""Test suite for phlcon_differential."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import phldef_conduit
import phlsys_conduit

import phlcon_differential

# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] the 'accepted' status persists when a review is updated with a new diff
# [ C] the 'closed' status does not allow revisions to be updated
# [ C] the 'closed' status does allow revisions to be closed again
# [ D] can detect 'missing testplan', 'invalid reviewer' parse errors
# [ E] commit messages with reviewers as the title are handled
# [  ] TODO
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_AcceptedPersistsWhenUpdated
# [ C] test_C_CantUpdateClosedReviews
# [ D] test_D_DistinguishParseErrors
# [ E] test_E_HandleReviewersAsTitle
# TODO
# =============================================================================

_COMMIT_MESSAGE_FORMAT = """
{title}

{summary}

Test Plan: {test_plan}

Reviewers: {reviewers}
""".strip()


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.conduit = None
        self.reviewerConduit = None
        self.phabConduit = None
        self.test_data = None

    def setUp(self):
        self.test_data = phldef_conduit
        self.conduit = phlsys_conduit.Conduit(
            self.test_data.TEST_URI,
            self.test_data.ALICE.user,
            self.test_data.ALICE.certificate)

        self.reviewerConduit = phlsys_conduit.Conduit(
            self.test_data.TEST_URI,
            self.test_data.BOB.user,
            self.test_data.BOB.certificate)

        self.phabConduit = phlsys_conduit.Conduit(
            self.test_data.TEST_URI,
            self.test_data.PHAB.user,
            self.test_data.PHAB.certificate)

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        rev_id = self._createNonEmptyRevision('test_A_Breathing')
        conduit = self.phabConduit
        phlcon_differential.create_inline_comment(
            conduit, rev_id, 'readme', 2, 'this is an inline comment')
        phlcon_differential.create_inline_comment(
            conduit, rev_id, 'readme', 3, 'this another inline comment')
        phlcon_differential.create_comment(
            conduit, rev_id, 'this is a message', attach_inlines=True)

    def test_B_AcceptedPersistsWhenUpdated(self):
        conduit = self.phabConduit
        author = phldef_conduit.ALICE.user
        reviewer = phldef_conduit.BOB.user
        with phlsys_conduit.act_as_user_context(conduit, author):
            revision = phlcon_differential.create_empty_revision(conduit)
        with phlsys_conduit.act_as_user_context(conduit, reviewer):
            phlcon_differential.create_comment(
                conduit,
                revision,
                action=phlcon_differential.Action.accept)
        with phlsys_conduit.act_as_user_context(conduit, author):
            phlcon_differential.update_revision_empty(conduit, revision)
        self.assertEqual(
            phlcon_differential.get_revision_status(conduit, revision),
            phlcon_differential.ReviewStates.accepted)

    def test_C_CantUpdateClosedReviews(self):
        conduit = self.phabConduit
        author = phldef_conduit.ALICE.user
        reviewer = phldef_conduit.BOB.user
        with phlsys_conduit.act_as_user_context(conduit, author):
            revision = phlcon_differential.create_empty_revision(conduit)
        with phlsys_conduit.act_as_user_context(conduit, reviewer):
            phlcon_differential.create_comment(
                conduit,
                revision,
                action=phlcon_differential.Action.accept)
        with phlsys_conduit.act_as_user_context(conduit, author):
            phlcon_differential.create_comment(
                conduit,
                revision,
                action=phlcon_differential.Action.close)
            self.assertRaises(
                phlcon_differential.UpdateClosedRevisionError,
                phlcon_differential.update_revision_empty,
                conduit,
                revision)

            # expect that we can close a closed revision without errors
            phlcon_differential.close(conduit, revision)

    def _make_commit_message(self, title, summary, test_plan, reviewer_list):
        return _COMMIT_MESSAGE_FORMAT.format(
            title=title,
            summary=summary,
            test_plan=test_plan,
            reviewers=" ".join(reviewer_list))

    def test_D_DistinguishParseErrors(self):
        not_a_username1 = 'NOTAUSER1_test_D_DistinguishParseErrors'
        not_a_username2 = 'NOTAUSER2_test_D_DistinguishParseErrors'

        title = ""
        summary = ""
        test_plan = ""
        unknown_reviewers = [
            not_a_username1,
            not_a_username2,
            phldef_conduit.NOTAUSER.user]
        reviewers = [phldef_conduit.ALICE.user]

        message = self._make_commit_message(
            title, summary, test_plan, reviewers + unknown_reviewers)

        parsed = phlcon_differential.parse_commit_message(
            self.conduit, message)

        parsed_errors = phlcon_differential.parse_commit_message_errors(
            parsed.errors)

        self.assertEqual(parsed.fields["title"], title)
        self.assertEqual(parsed.fields["summary"], summary)
        self.assertEqual(parsed.fields["testPlan"], test_plan)
        self.assertListEqual(parsed.fields["reviewerPHIDs"], [])

        def all_are_instance_of(item_list, kind):
            return all([isinstance(x, kind) for x in item_list])

        def only_one_is_instance_of(item_list, kind):
            # iterate to the first one and then make sure there are no others
            i = iter([isinstance(x, kind) for x in item_list])
            return any(i) and not any(i)

        self.assertTrue(
            all_are_instance_of(
                parsed_errors,
                phlcon_differential.ParseCommitMessageFail))

        self.assertTrue(
            only_one_is_instance_of(
                parsed_errors,
                phlcon_differential.ParseCommitMessageNoTestPlanFail))

        self.assertTrue(
            only_one_is_instance_of(
                parsed_errors,
                phlcon_differential.ParseCommitMessageUnknownReviewerFail))

        self.assertTrue(
            only_one_is_instance_of(
                parsed_errors,
                phlcon_differential.ParseCommitMessageUnknownFail))

        UnkReviewer = phlcon_differential.ParseCommitMessageUnknownReviewerFail
        did_test = False
        for error in parsed_errors:
            if isinstance(error, UnkReviewer):
                self.assertSetEqual(
                    set(error.user_list), set(unknown_reviewers))
                did_test = True

        self.assertTrue(did_test)

    def test_E_HandleReviewersAsTitle(self):
        message = """Reviewers: alice

        Here is the real title.
        """

        # this should give us an UnknownParseCommitMessageResponseError
        self.assertRaises(
            phlcon_differential.UnknownParseCommitMessageResponseError,
            phlcon_differential.parse_commit_message,
            self.conduit,
            message)

    def testNullQuery(self):
        phlcon_differential.query(self.conduit)

    def testParseCommitMessage(self):
        title = "this is the title"
        summary = "this is the summary"
        test_plan = "this is the test plan"
        reviewers = "bob"
        message = ""
        message += title + "\n"
        message += "\n"
        message += summary + "\n"
        message += "Test Plan: " + test_plan + "\n"
        message += "Reviewers: " + reviewers + "\n"
        diff = phlcon_differential
        diff.parse_response = diff.parse_commit_message(
            self.conduit, message)
        self.assertEqual(diff.parse_response.fields["title"], title)
        self.assertEqual(diff.parse_response.fields["summary"], summary)
        self.assertEqual(diff.parse_response.fields["testPlan"], test_plan)
        # XXX: can't check reviewerPHIDs at this point

    def testCreateCloseRawDiffRevision(self):
        diff = """
diff --git a/readme b/readme
index d4711bb..ee5b241 100644
--- a/readme
+++ b/readme
@@ -7,3 +7,4 @@ and one more!!
 -- and one last(?) one
 alaric!
 local stuff!
+manual conduit submission
"""
        message = """
add a line to README

Test Plan: I proof-read it and it looked ok
"""

        diff2 = """
diff --git a/readme b/readme
index d4711bb..1c634f5 100644
--- a/readme
+++ b/readme
@@ -7,3 +7,5 @@ and one more!!
 -- and one last(?) one
 alaric!
 local stuff!
+manual conduit submission
+another line
"""

        diff_response = phlcon_differential.create_raw_diff(self.conduit, diff)

        parse_response = phlcon_differential.parse_commit_message(
            self.conduit, message)
        self.assertEqual(len(parse_response.errors), 0)

        create_response = phlcon_differential.create_revision(
            self.conduit, diff_response.id, parse_response.fields)

        query_response_list = phlcon_differential.query(
            self.conduit, [create_response.revisionid])
        self.assertEqual(len(query_response_list), 1)
        self.assertEqual(query_response_list[0].uri, create_response.uri)
        self.assertEqual(query_response_list[0].id, create_response.revisionid)
        self.assertEqual(
            query_response_list[0].status,
            phlcon_differential.ReviewStates.needs_review)

        diff2_response = phlcon_differential.create_raw_diff(
            self.conduit, diff2)

        update_response = phlcon_differential.update_revision(
            self.conduit,
            create_response.revisionid, diff2_response.id,
            parse_response.fields, "updated with new diff")
        self.assertEqual(
            update_response.revisionid, create_response.revisionid)
        self.assertEqual(update_response.uri, create_response.uri)

        comment_response = phlcon_differential.create_comment(
            self.reviewerConduit, create_response.revisionid, action="accept")
        self.assertEqual(
            comment_response.revisionid, create_response.revisionid)
        self.assertEqual(comment_response.uri, create_response.uri)

        query_response_list = phlcon_differential.query(
            self.conduit, [create_response.revisionid])
        self.assertEqual(len(query_response_list), 1)
        self.assertEqual(query_response_list[0].uri, create_response.uri)
        self.assertEqual(query_response_list[0].id, create_response.revisionid)
        self.assertEqual(
            query_response_list[0].status,
            phlcon_differential.ReviewStates.accepted)

        phlcon_differential.close(self.conduit, create_response.revisionid)

        query_response_list = phlcon_differential.query(
            self.conduit, [create_response.revisionid])
        self.assertEqual(len(query_response_list), 1)
        self.assertEqual(query_response_list[0].uri, create_response.uri)
        self.assertEqual(query_response_list[0].id, create_response.revisionid)
        self.assertEqual(
            query_response_list[0].status,
            phlcon_differential.ReviewStates.closed)

    def _createRevision(self, title):
        diff = """diff --git a/ b/"""
        message = title + "\n\ntest plan: no test plan"
        diff_response = phlcon_differential.create_raw_diff(self.conduit, diff)
        parse_response = phlcon_differential.parse_commit_message(
            self.conduit, message)
        create_response = phlcon_differential.create_revision(
            self.conduit, diff_response.id, parse_response.fields)
        return create_response.revisionid

    def _createNonEmptyRevision(self, title):
        diff = """
diff --git a/readme b/readme
index d4711bb..ee5b241 100644
--- a/readme
+++ b/readme
@@ -7,3 +7,4 @@ and one more!!
 -- and one last(?) one
 alaric!
 local stuff!
+manual conduit submission
"""

        message = "{}\n\nTest Plan: this is the plan".format(title)

        diff_response = phlcon_differential.create_raw_diff(self.conduit, diff)

        parse_response = phlcon_differential.parse_commit_message(
            self.conduit, message)
        self.assertEqual(len(parse_response.errors), 0)

        create_response = phlcon_differential.create_revision(
            self.conduit, diff_response.id, parse_response.fields)

        return create_response.revisionid

    def _authorCommentAction(self, revisionid, action):
        phlcon_differential.create_comment(
            self.conduit, revisionid, action=action)

    def _reviewCommentAction(self, revisionid, action):
        phlcon_differential.create_comment(
            self.reviewerConduit, revisionid, action=action)

    def _getState(self, revisionid):
        return phlcon_differential.query(self.conduit, [revisionid])[0].status

    def _authorActExp(self, revisionid, action, state):
        self._authorCommentAction(revisionid, action)
        self.assertEqual(self._getState(revisionid), state)

    def _reviewActExp(self, revisionid, action, state):
        self._reviewCommentAction(revisionid, action)
        self.assertEqual(self._getState(revisionid), state)

    def testReviewStates(self):
        revisionid = self._createRevision("testReviewStates")

        d = phlcon_differential
        authorActExp = self._authorActExp
        reviewActExp = self._reviewActExp

        states = phlcon_differential.ReviewStates

        authorActExp(revisionid, d.Action.rethink, states.needs_revision)
        authorActExp(revisionid, d.Action.request, states.needs_review)
        authorActExp(revisionid, d.Action.abandon, states.abandoned)
        authorActExp(revisionid, d.Action.reclaim, states.needs_review)

        reviewActExp(revisionid, d.Action.reject, states.needs_revision)
        reviewActExp(revisionid, d.Action.accept, states.accepted)
        reviewActExp(revisionid, d.Action.reject, states.needs_revision)
        reviewActExp(revisionid, d.Action.accept, states.accepted)

        authorActExp(revisionid, d.Action.close, states.closed)

    def testUpdateNoFields(self):
        revisionid = self._createRevision("testUpdateNoFields")
        diff = """diff --git a/ b/"""
        diff_response = phlcon_differential.create_raw_diff(self.conduit, diff)
        phlcon_differential.update_revision(
            self.conduit, revisionid, diff_response.id, [], "update")

    def testUpdateStrangeFields(self):
        revisionid = self._createRevision("testUpdateStrangeFields")
        message = "test\n\nmeh: blah\nstrange: blah\n123: blah\ntest plan: hmm"
        diff = """diff --git a/ b/"""
        diff_response = phlcon_differential.create_raw_diff(self.conduit, diff)
        parse_response = phlcon_differential.parse_commit_message(
            self.conduit, message)
        print(str(parse_response.fields))
        phlcon_differential.update_revision(
            self.conduit,
            revisionid,
            diff_response.id,
            parse_response.fields,
            "update")
        # TODO: check that the strange fields appear in the summary field

    def testCanGetCommitMessage(self):
        revisionid = self._createRevision("testUpdateStrangeFields")
        phlcon_differential.get_commit_message(self.conduit, revisionid)

    def testCreateUpdateEmptyRevision(self):
        conduit = phlsys_conduit.Conduit(
            self.test_data.TEST_URI,
            self.test_data.PHAB.user,
            self.test_data.PHAB.certificate)
        author = phldef_conduit.ALICE.user
        with phlsys_conduit.act_as_user_context(conduit, author):
            revision_id = phlcon_differential.create_empty_revision(conduit)

        revision_list = phlcon_differential.query(conduit, [revision_id])
        self.assertEqual(len(revision_list), 1)

        with phlsys_conduit.act_as_user_context(conduit, author):
            phlcon_differential.update_revision_empty(conduit, revision_id)

    # XXX: re-instate when we have support for reviewers and ccs
    # def testCreateEmptyRevisionReviewersCcs(self):
    #     id = abdt_conduit.create_empty_revision(
    #         self.conduit,
    #         self.test_data.alice.user,
    #         [self.test_data.bob.user],
    #         [self.test_data.phab.user])
    #     revision_list = phlcon_differential.query(self.conduit, [id])
    #     self.assertEqual(len(revision_list), 1)


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
