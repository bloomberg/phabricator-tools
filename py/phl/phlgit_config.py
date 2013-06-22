"""Wrapper around 'git config'"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_config
#
# Public Classes:
#   Test
#
# Public Functions:
#   set_username_email
#   get_username
#   get_email
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import unittest

import phlsys_git
import phlsys_subprocess


def set_username_email(clone, username, email):
    """Set the user.name and user.email on the supplied git clone.

    :clone: the clone to operate on
    :username: the string value for user.name
    :email: the string value for user.email
    :returns: None

    """
    clone.call("config", "user.name", username)
    clone.call("config", "user.email", email)


def get_username(clone):
    """Return the string username for the current clone.

    :clone: the clone to operate on
    :returns: string username for the current clone

    """
    return clone.call("config", "--get", "user.name").strip()


def get_email(clone):
    """Return the string email for the current clone.

    :clone: the clone to operate on
    :returns: string email for the current clone

    """
    return clone.call("config", "--get", "user.email").strip()


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.path = "phlgit_diff_TestDiff"
        self.clone = None

    def setUp(self):
        # TODO: make this more portable with shutil etc.
        phlsys_subprocess.run_commands("mkdir " + self.path)
        phlsys_subprocess.run("git", "init", workingDir=self.path)
        self.clone = phlsys_git.GitClone(self.path)

    def testCanSetAndGetUsernameEmail(self):
        testUsername = "test"
        testEmail = "test@server.fake"
        set_username_email(self.clone, testUsername, testEmail)
        self.assertEqual(get_username(self.clone), testUsername)
        self.assertEqual(get_email(self.clone), testEmail)

    def testCanSetAndGetUsernameEmailTwice(self):
        testUsername = "test"
        testUsername2 = "another test username"
        testEmail = "test@server.fake"
        testEmail2 = "another.test.username@server.fake"
        set_username_email(self.clone, testUsername, testEmail)
        self.assertEqual(get_username(self.clone), testUsername)
        self.assertEqual(get_email(self.clone), testEmail)
        set_username_email(self.clone, testUsername2, testEmail2)
        self.assertEqual(get_username(self.clone), testUsername2)
        self.assertEqual(get_email(self.clone), testEmail2)

    def tearDown(self):
        phlsys_subprocess.run_commands("rm -rf " + self.path)


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
