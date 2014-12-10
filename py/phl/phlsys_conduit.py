"""Wrapper to call Phabricator's Conduit API."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_conduit
#
# Public Classes:
#   ConduitException
#   Conduit
#    .set_act_as_user
#    .clear_act_as_user
#    .get_act_as_user
#    .conduit_uri
#    .raw_call
#    .ping
#   MultiConduit
#    .call_as_user
#    .conduit_uri
#   CallMultiConduitAsUser
#
# Public Functions:
#   act_as_user_context
#   make_conduit_uri
#   make_phab_test_conduit
#
# Public Assignments:
#   SESSION_ERROR
#   CONDUITPROXY_ERROR_CONNECT
#   CONDUITPROXY_ERROR_BADAUTH
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import hashlib
import json
import logging
import time
import urllib
import urllib2
import urlparse

import phldef_conduit

import phlsys_multiprocessing

_URLLIB_TIMEOUT = 600

# TODO: handle re-authentication when the token expires
# TODO: allow connections without specifying user details where possible


@contextlib.contextmanager
def act_as_user_context(conduit, user):
    """Manage the context of impersonating another user.

    Restore the original act_as_user_context value when the context expires
    or if an exception is raised.  The context manager itself is exception
    neutral.

    Usage Example:
        impersonate alice
        >>> conduit = make_phab_test_conduit()
        >>> with act_as_user_context(conduit, 'alice'):\
                conduit("user.whoami")["userName"]
        u'alice'

        impersonate bob
        >>> conduit = make_phab_test_conduit()
        >>> with act_as_user_context(conduit, 'bob'):\
                conduit("user.whoami")["userName"]
        u'bob'

        impersonate bob, revert to phab when context expires
        >>> conduit = make_phab_test_conduit()
        >>> with act_as_user_context(conduit, 'bob'): pass
        >>> conduit("user.whoami")["userName"]
        u'phab'

    """
    prevUser = conduit.get_act_as_user()
    try:
        conduit.set_act_as_user(user)
        yield conduit
    finally:
        if prevUser:
            conduit.set_act_as_user(prevUser)
        else:
            conduit.clear_act_as_user()


def make_conduit_uri(uri):
    """Return the expected conduit uri based on the supplied 'uri'.

    Usage examples:
        >>> make_conduit_uri('http://127.0.0.1')
        'http://127.0.0.1/api/'

        >>> make_conduit_uri('http://127.0.0.1/')
        'http://127.0.0.1/api/'

        >>> make_conduit_uri('http://127.0.0.1/conduit/')
        'http://127.0.0.1/api/'

    :uri: a uri to the Phabricator instance
    :returns: the expected conduit uri

    """
    url = urlparse.urlparse(uri)
    # pylint: disable=E1101
    expected = url.scheme + "://" + url.netloc + "/api/"
    # pylint: enable=E1101
    return expected


def make_phab_test_conduit():
    """Return a new Conduit constructed from phldef_conduit test_uri and phab.

    :returns: a new Conduit constructed from phldef_conduit test_uri and phab

    """
    test_data = phldef_conduit
    return Conduit(
        test_data.TEST_URI,
        test_data.PHAB.user,
        test_data.PHAB.certificate)


class ConduitException(Exception):

    def __init__(self, method, error, errormsg, result, obj, uri, actAsUser):
        """Construct from an error returned by conduit.

        :method: the conduit method that was being called
        :error: the type of error
        :message: the error message
        :response: the response field (expected to be empty)
        :obj: the object that was passed to conduit
        :uri: the URI to conduit
        :actAsUser: user that was being impersonated or None

        """
        message = (
            "phlsys_conduit.Conduit\n" +
            "method: '" + str(method) + "'\n" +
            "error: '" + str(error) + "'\n" +
            "errormsg: '" + str(errormsg) + "'\n" +
            "result: '" + str(result) + "'\n" +
            "object: '" + str(obj) + "'\n" +
            "uri: '" + str(uri) + "'\n" +
            "actAsUser: '" + str(actAsUser) + "'\n")
        super(ConduitException, self).__init__(message)
        self.method = method
        self.error = error
        self.errormsg = errormsg
        self.result = result
        self.obj = obj
        self.uri = uri
        self.actAsUser = actAsUser

# we would expect this to arise normally from time to time
SESSION_ERROR = "ERR-INVALID-SESSION"

# if we try to conduit.connect to a conduitproxy then we'll get this error,
# this means we should send the full cert every time.
CONDUITPROXY_ERROR_CONNECT = "CONDUITPROXY-ERR-REDUNDANT-CONNECT"

CONDUITPROXY_ERROR_BADAUTH = "CONDUITPROXY-ERR-BADAUTH"


class Conduit(object):

    # TODO: make this configurable
    testUri = phldef_conduit.TEST_URI

    def __init__(
            self,
            conduitUri,
            user=None,
            certificate=None,
            actAsUser=None,
            http_proxy=None,
            https_proxy=None):
        self._conduit_uri = conduitUri
        self._act_as_user = actAsUser
        self._timeout = 5
        self._username = user
        self._certificate = certificate
        self._client = "phlsys_conduit"
        self._client_version = 1
        self._http_proxy = http_proxy
        self._https_proxy = https_proxy

        self._conduit = {}
        if user and certificate:
            self._authenticate()

    def set_act_as_user(self,  user):
        self._act_as_user = user
        self._conduit["actAsUser"] = self._act_as_user

    def clear_act_as_user(self):
        self._act_as_user = None
        del self._conduit["actAsUser"]

    def get_act_as_user(self):
        return self._act_as_user

    @property
    def conduit_uri(self):
        return self._conduit_uri

    def _authenticate(self):

        message_dict = self._authenticate_make_message()
        method = "conduit.connect"

        response = self._communicate(method, message_dict)

        error = response["error_code"]
        error_message = response["error_info"]
        result = response["result"]

        is_conduitproxy = False

        if error:
            if error == CONDUITPROXY_ERROR_CONNECT:
                is_conduitproxy = True
            else:
                raise ConduitException(
                    method=method,
                    error=error,
                    errormsg=error_message,
                    result=result,
                    obj=message_dict,
                    uri=self._conduit_uri,
                    actAsUser=self._act_as_user)

        if is_conduitproxy:
            # conduit proxies don't have sessions, send the cert every time
            self._conduit = {
                'user': self._username,
                'cert': self._certificate
            }
        else:
            self._conduit = {
                'sessionKey': result["sessionKey"],
                'connectionID': result["connectionID"],
            }

        if self._act_as_user:
            self._conduit["actAsUser"] = self._act_as_user

    def _authenticate_make_message(self):
        token = str(int(time.time()))
        # pylint: disable=E1101
        signature = hashlib.sha1(token + self._certificate).hexdigest()
        # pylint: enable=E1101

        return {
            "user": self._username,
            "host": self._conduit_uri,
            "client": self._client,
            "clientVersion": self._client_version,
            "authToken": token,
            "authSignature": signature,
        }

    def _communicate(self, method, message_dict):
        path = self._conduit_uri + method

        params = json.dumps(message_dict)

        body = urllib.urlencode({
            "params": params,
            "output": "json",
        })

        if self._https_proxy or self._http_proxy:
            proxy = {}
            if self._https_proxy:
                proxy['https'] = self._https_proxy
            if self._http_proxy:
                proxy['http'] = self._http_proxy
            proxy_handler = urllib2.ProxyHandler(proxy)
            opener = urllib2.build_opener(proxy_handler)
            data = opener.open(path, body, _URLLIB_TIMEOUT).read()
        else:
            data = urllib2.urlopen(path, body, _URLLIB_TIMEOUT).read()

        return json.loads(data)

    def __call__(self, method, param_dict_in=None):
        return self.raw_call(method, param_dict_in)["result"]

    def raw_call(self, method, param_dict_in=None):
        attempts = 3
        for x in range(attempts):
            param_dict = dict(param_dict_in) if param_dict_in else {}
            param_dict["__conduit__"] = self._conduit
            response = self._communicate(method, param_dict)

            error = response["error_code"]
            error_message = response["error_info"]
            result = response["result"]

            if not error:
                break
            else:
                if error == SESSION_ERROR:
                    logging.warning(
                        "phlsys_conduit: SESSION-ERROR (try {0})".format(x))
                    self._authenticate()
                else:
                    raise ConduitException(
                        method=method,
                        error=error,
                        errormsg=error_message,
                        result=result,
                        obj=param_dict,
                        uri=self._conduit_uri,
                        actAsUser=self._act_as_user)

        if error:
            raise ConduitException(
                method=method,
                error=error,
                errormsg=error_message,
                result=result,
                obj=param_dict,
                uri=self._conduit_uri,
                actAsUser=self._act_as_user)

        return response

    def ping(self):
        return self("conduit.ping")


class MultiConduit(object):

    """A conduit that supports multi-processing."""

    def __init__(self, *args, **kwargs):

        def factory():
            return Conduit(*args, **kwargs)

        # Phabricator supports 5 simultaneous connections per user
        # by default:
        #
        #   conf/default.conf.php:  'auth.sessions.conduit'       => 5,
        #
        max_sessions_per_user = 5
        self._conduits = phlsys_multiprocessing.MultiResource(
            max_sessions_per_user, factory)

    def call_as_user(self, user, *args, **kwargs):
        with self._conduits.resource_context() as conduit:
            with act_as_user_context(conduit, user):
                return conduit(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        with self._conduits.resource_context() as conduit:
            return conduit(*args, **kwargs)

    @property
    def conduit_uri(self):
        with self._conduits.resource_context() as conduit:
            return conduit.conduit_uri


class CallMultiConduitAsUser(object):

    """A proxy for calling a MultiConduit as a particular user."""

    def __init__(self, conduit, as_user):
        super(CallMultiConduitAsUser, self).__init__()
        self._conduit = conduit
        self._as_user = as_user

    def __call__(self, *args, **kwargs):
        return self._conduit.call_as_user(self._as_user, *args, **kwargs)


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
