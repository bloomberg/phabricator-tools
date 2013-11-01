"""Wrapper to call Phabricator's users Conduit API."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_user
#
# Public Functions:
#   is_no_such_error
#   query_user_from_email
#   query_users_from_emails
#   query_users_from_phids
#   query_users_from_usernames
#   query_usernames_from_phids
#   make_username_phid_dict
#   make_phid_username_dict
#
# Public Assignments:
#   QueryResponse
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlsys_conduit
import phlsys_namedtuple


QueryResponse = phlsys_namedtuple.make_named_tuple(
    'phlcon_user__QueryResponse',
    required=['phid', 'userName', 'realName', 'image', 'uri', 'roles'],
    defaults={},
    ignored=['currentStatus', 'currentStatusUntil'])


def is_no_such_error(e):
    """Return True if the supplied ConduitException is due to unknown user.

    :e: a ConduitException
    :returns: True if the supplied ConduitException is due to unknown user

    """
    errConduitCore = "ERR-CONDUIT-CORE"
    noSuchEmail = ""
    noSuchEmail += "Array for %Ls conversion is empty. "
    noSuchEmail += "Query: SELECT * FROM %s WHERE userPHID IN (%Ls) "
    noSuchEmail += "AND UNIX_TIMESTAMP() BETWEEN dateFrom AND dateTo %Q"
    return e.error == errConduitCore and e.errormsg == noSuchEmail


def query_user_from_email(conduit, email):
    """Return a QueryResponse based on the provided email.

    If the email does not correspond to a username then return None.

    :conduit: must support 'call()' like phlsys_conduit
    :email: an email address as a string
    :returns: a QueryResponse or None

    """
    d = {"emails": [email], "limit": 1}
    response = None
    try:
        response = conduit.call("user.query", d)
    except phlsys_conduit.ConduitException as e:
        if not is_no_such_error(e):
            raise

    if response:
        if len(response) != 1:
            raise Exception("unexpected number of entries")
        return QueryResponse(**response[0])
    else:
        return None


def query_users_from_emails(conduit, emails):
    """Return a list of username strings based on the provided emails.

    If an email does not correspond to a username then None is inserted in
    its place.

    :conduit: must support 'call()' like phlsys_conduit
    :emails: a list of strings corresponding to user email addresses
    :returns: a list of strings corresponding to Phabricator usernames

    """
    users = []
    for e in emails:
        u = query_user_from_email(conduit, e)
        if u is not None:
            users.append(u.userName)
        else:
            users.append(None)
    return users


def query_users_from_phids(conduit, phids):
    """Return a list of QueryResponse based on the provided phids.

    If a phid does not correspond to a username then return None.

    :conduit: must support 'call()' like phlsys_conduit
    :phids: a list of strings corresponding to user phids
    :returns: a list of QueryResponse

    """
    if not isinstance(phids, list):
        raise ValueError("phids must be a list")
    d = {"phids": phids, "limit": len(phids)}

    try:
        response = conduit.call("user.query", d)
    except phlsys_conduit.ConduitException as e:
        if not is_no_such_error(e):
            raise
        return None
    else:
        if len(response) != len(phids):
            raise Exception("unexpected number of entries\n" + str(response))

    return [QueryResponse(**u) for u in response]


def query_users_from_usernames(conduit, usernames):
    """Return a list of QueryResponse based on the provided usernames.

    Return None if any of 'usernames' is invalid.

    :conduit: must support 'call()' like phlsys_conduit
    :usernames: a list of strings corresponding to usernames
    :returns: a list of QueryResponse

    """
    assert isinstance(usernames, list)
    d = {"usernames": usernames, "limit": len(usernames)}

    response = None
    try:
        response = conduit.call("user.query", d)
    except phlsys_conduit.ConduitException as e:
        if not is_no_such_error(e):
            raise

    if response is None:
        return None

    if len(response) != len(usernames):
        raise Exception("unexpected number of entries")

    return [QueryResponse(**u) for u in response]


def query_usernames_from_phids(conduit, phids):
    """Return a list of username strings based on the provided phids.

    If a phid does not correspond to a username then raise.

    :conduit: must support 'call()' like phlsys_conduit
    :phids: a list of strings corresponding to user phids
    :returns: a list of strings corresponding to Phabricator usernames

    """
    usernames = [u.userName for u in query_users_from_phids(conduit, phids)]
    return usernames


def make_username_phid_dict(conduit, usernames):
    """Return a dictionary of usernames to phids.

    Return None if any of 'usernames' is invalid.

    :conduit: must support 'call()' like phlsys_conduit
    :usernames: a list of strings corresponding to Phabricator usernames
    :returns: a dictionary of usernames to corresponding phids

    """
    users = query_users_from_usernames(conduit, usernames)
    if users is None:
        return None
    else:
        return {u.userName: u.phid for u in users}


def make_phid_username_dict(conduit, phids):
    """Return a dictionary of phids to usernames.

    Return None if any of 'phids' is invalid.

    :conduit: must support 'call()' like phlsys_conduit
    :phids: a list of strings corresponding to Phabricator PHIDs
    :returns: a dictionary of usernames to corresponding phids

    """
    users = query_users_from_phids(conduit, phids)
    if users is None:
        return None
    else:
        return {u.phid: u.userName for u in users}


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
