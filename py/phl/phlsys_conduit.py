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
#    .get_user
#    .conduit_uri
#    .call
#    .ping
#
# Public Functions:
#   act_as_user_context
#   make_conduit_uri
#   make_phab_test_conduit
#
# Public Assignments:
#   SESSION_ERROR
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
                conduit.call("user.whoami")["userName"]
        u'alice'

        impersonate bob
        >>> conduit = make_phab_test_conduit()
        >>> with act_as_user_context(conduit, 'bob'):\
                conduit.call("user.whoami")["userName"]
        u'bob'

        impersonate bob, revert to phab when context expires
        >>> conduit = make_phab_test_conduit()
        >>> with act_as_user_context(conduit, 'bob'): pass
        >>> conduit.call("user.whoami")["userName"]
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

    def get_user(self):
        return self._username

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

        if error:
            raise ConduitException(
                method=method,
                error=error,
                errormsg=error_message,
                result=result,
                obj=message_dict,
                uri=self._conduit_uri,
                actAsUser=self._act_as_user)

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

    def call(self, method, param_dict_in=None):
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

        return result

    def ping(self):
        return self.call("conduit.ping")


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
