"""Test suite for abdt_conduit."""
#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [  ] TODO
#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
#==============================================================================

import unittest

import phlcon_differential
import phldef_conduit
import phlsys_conduit

import abdt_conduit
import abdt_exception


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.test_data = None
        self.sys_conduit = None
        self.conduit = None
        self.empty_diff = "diff --git a/ b/"

    def setUp(self):
        self.test_data = phldef_conduit
        self.sys_conduit = phlsys_conduit.Conduit(
            self.test_data.TEST_URI,
            self.test_data.PHAB.user,
            self.test_data.PHAB.certificate)
        self.conduit = abdt_conduit.Conduit(self.sys_conduit)

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        # generally exercise all of the conduit methods
        alice = self.test_data.ALICE.user
        bob = self.test_data.BOB.user
        revision = self.conduit.create_empty_revision_as_user(bob)
        self.conduit.create_comment(revision, 'test comment')
        self.conduit.create_comment(
            revision, 'silent test comment', silent=True)
        self.conduit.get_commit_message(revision)
        self.assertFalse(self.conduit.is_review_accepted(revision))
        self.conduit.set_requires_revision(revision)
        self.assertFalse(self.conduit.is_review_accepted(revision))
        self.conduit.accept_revision_as_user(revision, alice)
        self.assertTrue(self.conduit.is_review_accepted(revision))
        self.conduit.set_requires_revision(revision)
        self.assertFalse(self.conduit.is_review_accepted(revision))
        self.conduit.accept_revision_as_user(revision, alice)

        # check that the review is still accepted after an update
        self.assertTrue(self.conduit.is_review_accepted(revision))
        self.conduit.update_revision(revision, self.empty_diff, 'update')
        self.assertTrue(self.conduit.is_review_accepted(revision))

        self.conduit.abandon_revision(revision)

        # un-abandon
        with phlsys_conduit.act_as_user_context(self.sys_conduit, bob):
            phlcon_differential.create_comment(
                self.sys_conduit,
                revision,
                action=phlcon_differential.Action.reclaim)

        self.conduit.commandeer_revision_as_user(revision, alice)
        self.conduit.commandeer_revision_as_user(revision, bob)

        # close non-accepted revision
        # self.conduit.set_requires_revision(revision)
        # self.assertFalse(self.conduit.is_review_accepted(revision))
        # self.conduit.close_revision(revision)
        # self.assertFalse(self.conduit.is_review_accepted(revision))

        # close revision
        self.conduit.accept_revision_as_user(revision, alice)
        self.assertTrue(self.conduit.is_review_accepted(revision))
        self.conduit.close_revision(revision)

        # commandeer closed revision
        # self.conduit.commandeer_revision_as_user(revision, alice)

        # update closed revision
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
