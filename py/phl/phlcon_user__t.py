"""Test suite for phlcon_user"""

import unittest

import phlcon_user
import phldef_conduit
import phlsys_conduit

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# TODO
#------------------------------------------------------------------------------
# Tests:
# TODO
#==============================================================================


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

    def testBadPhid(self):
        bad_phid = "asd9f87"
        phidDict = phlcon_user.make_phid_username_dict(
            self.conduit, [bad_phid])
        self.assertIsNone(phidDict)

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
