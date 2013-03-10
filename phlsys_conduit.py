"""Wrapper to call Phabricator's Conduit API"""

import hashlib
import httplib
import json
import os
import time
import unittest
import urllib
import urlparse

import phldef_conduit

# TODO: handle re-authentication when the token expires
# TODO: allow connections without specifying user details where possible


class ConduitException(Exception):
    def __init__(self, method, error, errormsg, result, obj, uri, actAsUser):
        """Construct from an error returned by conduit

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
            "actAsUser: '" + str(uri) + "'\n")
        super(ConduitException, self).__init__(message)
        self.method = method
        self.error = error
        self.errormsg = errormsg
        self.result = result
        self.obj = obj
        self.uri = uri
        self.actAsUser = actAsUser


class Conduit():

    # TODO: make this configurable
    testUri = phldef_conduit.test_uri

    def __init__(self, conduitUri, user, certificate, actAsUser=None):
        self._conduit_uri = conduitUri
        self._act_as_user = actAsUser
        self._timeout = 5
        self._username = user
        self._certificate = certificate
        self._client = "phlsys_conduit"
        self._client_version = 1

        self._authenticate()

    @classmethod
    def setPathToArc(cls, path):
        if not os.path.isfile(path):
            raise Exception("not a valid file: " + path)
        cls._pathToArc = path

    def setActAsUser(self,  user):
        self._act_as_user = user
        self._conduit["actAsUser"] = self._act_as_user

    def clearActAsUser(self):
        self._act_as_user = None
        del self._conduit["actAsUser"]

    def _authenticate(self):

        token = str(int(time.time()))
        signature = hashlib.sha1(token + self._certificate).hexdigest()

        message_dict = {
            "user": self._username,
            "host": self._conduit_uri,
            "client": self._client,
            "clientVersion": self._client_version,
            "authToken": token,
            "authSignature": signature,
        }

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

    def _communicate(self, method, message_dict):
        url = urlparse.urlparse(self._conduit_uri)

        if url.scheme == 'https':
            conn = httplib.HTTPSConnection(url.netloc, timeout=self._timeout)
        else:
            conn = httplib.HTTPConnection(url.netloc, timeout=self._timeout)

        path = url.path + method

        headers = {
            'User-Agent': 'python-phabricator/%s' % str(self._client_version),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        params = json.dumps(message_dict)

        body = urllib.urlencode({
            "params": params,
            "output": "json",
        })

        # TODO: Use HTTP "method" from interfaces.json
        conn.request('POST', path, body, headers)
        response = conn.getresponse()
        data = response.read()
        return json.loads(data)

    def call(self, method, param_dict_in=None):
        param_dict = dict(param_dict_in) if param_dict_in else {}
        param_dict["__conduit__"] = self._conduit
        response = self._communicate(method, param_dict)

        error = response["error_code"]
        error_message = response["error_info"]
        result = response["result"]
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


class TestConduit(unittest.TestCase):

    def testCanPing(self):
        test_data = phldef_conduit
        self.conduit = Conduit(
            test_data.test_uri,
            test_data.alice.user,
            test_data.alice.certificate)
        self.conduit.ping()

    def testCanListReviews(self):
        test_data = phldef_conduit
        self.conduit = Conduit(
            test_data.test_uri,
            test_data.alice.user,
            test_data.alice.certificate)
        self.conduit.ping()
        self.conduit.call("differential.query")

    def testRaisesOnNonAuth(self):
        test_data = phldef_conduit
        self.assertRaises(
            ConduitException,
            Conduit,
            test_data.test_uri,
            "dontcreateausercalledthis",
            test_data.alice.certificate)

    # TODO: test re-authentication when the token expires
    # TODO: need to test something that requires authentication
    # TODO: test raises on bad instanceUri

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
