"""Test suite for phlcon_user."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import phldef_conduit
import phlsys_conduit

import phlcon_user

# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# TODO
# -----------------------------------------------------------------------------
# Tests:
# TODO
# =============================================================================


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.conduit = None
        self.test_user = phldef_conduit.ALICE.user
        self.test_email = phldef_conduit.ALICE.email

    def setUp(self):
        test_data = phldef_conduit
        self.conduit = phlsys_conduit.Conduit(
            test_data.TEST_URI,
            test_data.ALICE.user,
            test_data.ALICE.certificate)

    def tearDown(self):
        pass

    def testAliceEmail(self):
        users = phlcon_user.query_users_from_emails(
            self.conduit, [self.test_email])
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.test_user)

        user = phlcon_user.query_user_from_email(self.conduit, self.test_email)
        self.assertEqual(user.userName, self.test_user)

        phidUsers = phlcon_user.query_users_from_phids(
            self.conduit, [user.phid])
        self.assertEqual(phidUsers[0].userName, self.test_user)

        phidUsernames = phlcon_user.query_usernames_from_phids(
            self.conduit, [user.phid])
        self.assertEqual(phidUsernames[0], self.test_user)

    def testAliceAndNooneEmail(self):
        emails = [self.test_email, "noone@server.invalid", "a@server.invalid"]
        users = phlcon_user.query_users_from_emails(self.conduit, emails)
        self.assertEqual(len(users), 3)
        self.assertListEqual(users, [self.test_user, None, None])

    def testAliceUsername(self):
        users = phlcon_user.query_users_from_usernames(
            self.conduit, [self.test_user])
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].userName, self.test_user)

        userDict = phlcon_user.make_username_phid_dict(
            self.conduit, [self.test_user])
        self.assertEqual(len(userDict), 1)
        self.assertEqual(userDict[self.test_user], users[0].phid)

        username = users[0].userName
        phid = users[0].phid
        phidDict = phlcon_user.make_phid_username_dict(self.conduit, [phid])
        self.assertEqual(len(phidDict), 1)
        self.assertEqual(phidDict[phid], username)

    def testBadUsername(self):
        bad_username = "#@)4308f:"
        users = phlcon_user.query_users_from_usernames(
            self.conduit, [bad_username])
        self.assertIsNone(users)

        userDict = phlcon_user.make_username_phid_dict(
            self.conduit, [bad_username])
        self.assertIsNone(userDict)

    def testAliceAndBadUsername(self):
        bad_username = "#@)4308f:"
        users = phlcon_user.query_users_from_usernames(
            self.conduit, [self.test_user, bad_username])
        self.assertIsNone(users)

        userDict = phlcon_user.make_username_phid_dict(
            self.conduit, [self.test_user, bad_username])
        self.assertIsNone(userDict)

    def testBadPhid(self):
        bad_phid = "asd9f87"
        phidDict = phlcon_user.make_phid_username_dict(
            self.conduit, [bad_phid])
        self.assertIsNone(phidDict)

    def testAliceAndBadPhid(self):
        users = phlcon_user.query_users_from_usernames(
            self.conduit, [self.test_user])
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].userName, self.test_user)

        bad_phid = "asd9f87"
        phidDict = phlcon_user.make_phid_username_dict(
            self.conduit, [users[0].phid, bad_phid])
        self.assertIsNone(phidDict)

    def testEmptyLists(self):
        users = phlcon_user.query_users_from_usernames(self.conduit, [])
        self.assertEqual(len(users), 0)

        users = phlcon_user.query_users_from_phids(self.conduit, [])
        self.assertEqual(len(users), 0)

        users = phlcon_user.query_usernames_from_phids(self.conduit, [])
        self.assertEqual(len(users), 0)

        users = phlcon_user.query_users_from_emails(self.conduit, [])
        self.assertEqual(len(users), 0)

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
