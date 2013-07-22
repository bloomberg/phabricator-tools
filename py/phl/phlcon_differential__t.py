"""Test suite for phlcon_differential."""

import unittest

import phldef_conduit
import phlsys_conduit

import phlcon_differential

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] the 'accepted' status persists when a review is updated with a new diff
# [ C] the 'closed' status does not allow revisions to be updated
# [  ] TODO
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_AcceptedPersistsWhenUpdated
# [ C] test_C_CantUpdateClosedReviews
# TODO
#==============================================================================


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
        pass

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

        get_diff_response = phlcon_differential._get_diff(
            self.conduit, diff_id=diff_response.id)
        self.assertEqual(get_diff_response.id, diff_response.id)

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

    def testCreateDiffRevision(self):
        diff = """
diff --git a/readme b/readme
index d4711bb..ee5b241 100644
--- a/readme
+++ b/readme
@@ -1,3 +1,4 @@ and one more!!
 -- and one last(?) one
 alaric!
 local stuff!
+manual conduit submission
"""
        message = """
add a line to README

Test Plan: I proof-read it and it looked ok
"""
        raw_diff_response = phlcon_differential.create_raw_diff(
            self.conduit, diff)
        get_diff_response = phlcon_differential._get_diff(
            self.conduit,
            diff_id=raw_diff_response.id)

        diff_response = phlcon_differential.create_diff(
            self.conduit,
            changes_dict=get_diff_response.changes,
            source_machine="test_machine",
            source_path="source_path",
            branch="branch",
            source_control_system="git",  # svn or git
            source_control_path="control_path",
            source_control_base_revision="0",
            lint_status="none",
            unit_status="none",
            bookmark=None,
            parent_revision_id=None,
            creation_method="arcanist daemon",
            author_phid=None,
            arcanist_project="project",
            repository_uuid=None)

        parse_response = phlcon_differential.parse_commit_message(
            self.conduit, message)
        self.assertEqual(len(parse_response.errors), 0)

        # rely on create_revision to raise if we get anything seriously wrong
        phlcon_differential.create_revision(
            self.conduit, diff_response["diffid"], parse_response.fields)

    def _createRevision(self, title):
        diff = """diff --git a/ b/"""
        message = title + "\n\ntest plan: no test plan"
        diff_response = phlcon_differential.create_raw_diff(self.conduit, diff)
        parse_response = phlcon_differential.parse_commit_message(
            self.conduit, message)
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
        print str(parse_response.fields)
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
            revision_id = phlcon_differential.update_revision_empty(
                conduit, revision_id)

    # XXX: re-instate when we have support for reviewers and ccs
    # def testCreateEmptyRevisionReviewersCcs(self):
    #     id = abdt_conduit.create_empty_revision(
    #         self.conduit,
    #         self.test_data.alice.user,
    #         [self.test_data.bob.user],
    #         [self.test_data.phab.user])
    #     revision_list = phlcon_differential.query(self.conduit, [id])
    #     self.assertEqual(len(revision_list), 1)


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
