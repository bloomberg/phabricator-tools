"""Wrapper to call Phabricator's users Conduit API"""

import collections
import unittest

import phlsys_conduit


def _makeNT(name, *fields):
    return collections.namedtuple('phlcon_user__' + name, fields)


QueryResponse = _makeNT(
    'QueryResponse',
    'phid', 'userName', 'realName', 'image', 'uri', 'roles')


def queryUserFromEmail(conduit, email):
    """Return a QueryResponse based on the provided emails.

    If the email does not correspond to a username then return None.

    :conduit: must support 'call()' like phlsys_conduit
    :email: an email address as a string
    :returns: a QueryResponse or None

    """
    d = {"emails": [email]}
    response = None
    try:
        response = conduit.call("user.query", d)
    except phlsys_conduit.ConduitException as e:
        errConduitCore = "ERR-CONDUIT-CORE"
        noSuchEmail = errConduitCore + ": "
        noSuchEmail += "Array for %Ls conversion is empty. "
        noSuchEmail += "Query: SELECT * FROM %s WHERE userPHID IN (%Ls) "
        noSuchEmail += "AND UNIX_TIMESTAMP() BETWEEN dateFrom AND dateTo %Q"
        if not(e.error == errConduitCore and e.errormsg == noSuchEmail):
            raise

    if response:
        if len(response) != 1:
            raise Exception("unexpected number of entries")
        return QueryResponse(**response[0])
    else:
        return None


def queryUsersFromEmails(conduit, emails):
    """Return a list of username strings based on the provided emails.

    If an email does not correspond to a username then None is inserted in
    its place.

    :conduit: must support 'call()' like phlsys_conduit
    :emails: a list of strings corresponding to user email addresses
    :returns: a list of strings corresponding to Phabricator usernames

    """
    users = []
    for e in emails:
        u = queryUserFromEmail(conduit, e)
        if u is not None:
            users.append(u.userName)
        else:
            users.append(None)
    return users


def queryUsersFromPhids(conduit, phids):
    """Return a list of QueryResponse based on the provided phids.

    If a phid does not correspond to a username then raise ValueError.

    :conduit: must support 'call()' like phlsys_conduit
    :phids: a list of strings corresponding to user phids
    :returns: a list of QueryResponse

    """
    if not isinstance(phids, list):
        raise ValueError("phids must be a list")
    d = {"phids": phids}
    response = conduit.call("user.query", d)

    if len(response) != len(phids):
        raise Exception("unexpected number of entries")

    return [QueryResponse(**u) for u in response]


def queryUsernamesFromPhids(conduit, phids):
    """Return a list of username strings based on the provided phids.

    If a phid does not correspond to a username then raise.

    :conduit: must support 'call()' like phlsys_conduit
    :phids: a list of strings corresponding to user phids
    :returns: a list of strings corresponding to Phabricator usernames

    """
    users = queryUsersFromPhids(conduit, phids)
    return [u.userName for u in users]


class TestUser(unittest.TestCase):

    def setUp(self):
        self.conduit = phlsys_conduit.Conduit(
            phlsys_conduit.Conduit.testUri)
        self.angelosEmail = "jevripio@bloomberg.net"

    def testAngelosEmail(self):
        users = queryUsersFromEmails(self.conduit, [self.angelosEmail])
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], 'angelos')

        user = queryUserFromEmail(self.conduit, self.angelosEmail)
        self.assertEqual(user.userName, 'angelos')

        phidUsers = queryUsersFromPhids(self.conduit, [user.phid])
        self.assertEqual(phidUsers[0].userName, 'angelos')

        phidUsernames = queryUsernamesFromPhids(self.conduit, [user.phid])
        self.assertEqual(phidUsernames[0], 'angelos')

    def testAngelosAndNooneEmail(self):
        emails = [self.angelosEmail, "noone@nowhere.com", "a@b.com"]
        users = queryUsersFromEmails(self.conduit, emails)
        self.assertEqual(len(users), 3)
        self.assertListEqual(users, ['angelos', None, None])

    def testAngelosLilitAndNooneEmail(self):
        emails = [
            self.angelosEmail,
            "noone@nowhere.com",
            "ldarbinyan@bloomberg.net",
            "a@b.com"]
        users = queryUsersFromEmails(self.conduit, emails)
        self.assertEqual(len(users), 4)
        self.assertListEqual(users, ['angelos', None, 'lilit', None])

    def testLilitAngelosAndNooneEmail(self):
        emails = [
            "ldarbinyan@bloomberg.net",
            "noone@nowhere.com",
            self.angelosEmail,
            "a@b.com"]
        users = queryUsersFromEmails(self.conduit, emails)
        self.assertEqual(len(users), 4)
        self.assertListEqual(users, ['lilit', None, 'angelos', None])


if __name__ == "__main__":
    unittest.main()

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
