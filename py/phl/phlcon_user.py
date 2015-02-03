"""Wrapper to call Phabricator's users Conduit API."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_user
#
# Public Classes:
#   UserPhidCache
#    .add_hint
#    .add_hint_list
#    .get_phid
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
from __future__ import division
from __future__ import print_function

import phlsys_conduit
import phlsys_namedtuple


QueryResponse = phlsys_namedtuple.make_named_tuple(
    'phlcon_user__QueryResponse',
    required=['phid', 'userName', 'realName', 'image', 'uri', 'roles'],
    defaults={},
    ignored=['currentStatus', 'currentStatusUntil'])


class UserPhidCache(object):

    """Efficiently retrieve the PHID for specified usernames."""

    def __init__(self, conduit):
        """Construct a cache attached to the specified 'conduit'."""
        super(UserPhidCache, self).__init__()
        self._user_to_phid = {}
        self._hinted_users = set()
        self._conduit = conduit

    def add_hint(self, user):
        """Register 'user' as a user we'll later query."""
        if user not in self._user_to_phid:
            self._hinted_users.add(user)

    def add_hint_list(self, user_list):
        """Register all 'user_list' as users we'll later query."""
        for user in user_list:
            self.add_hint(user)

    def get_phid(self, user):
        """Return the PHID for the specified 'user'."""
        self.add_hint(user)
        if user not in self._user_to_phid:
            results = make_username_phid_dict(
                self._conduit, list(self._hinted_users))
            self._user_to_phid.update(results)
            self._hinted_users = set()
        return self._user_to_phid[user]


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
        response = conduit("user.query", d)
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

    response = None
    try:
        response = conduit("user.query", d)
    except phlsys_conduit.ConduitException as e:
        if not is_no_such_error(e):
            raise
        return None

    if response and len(response) == len(phids):
        return [QueryResponse(**u) for u in response]
    else:
        return None


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
        response = conduit("user.query", d)
    except phlsys_conduit.ConduitException as e:
        if not is_no_such_error(e):
            raise

    if response and len(response) == len(usernames):
        return [QueryResponse(**u) for u in response]
    else:
        return None


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
