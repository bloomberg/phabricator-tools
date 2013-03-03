"""Wrapper to call Phabricator's Conduit API"""

import hashlib
import httplib
import json
import os
import time
import unittest
import urllib
import urlparse

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
    testUri = "http://127.0.0.1/api/"

    def __init__(self, conduitUri, actAsUser=None):
        self._conduitUri = conduitUri
        self._actAsUser = actAsUser
        self._timeout = 5
        self._username = "phab"
        self._certificate = "xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrvafgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf"
        self._client = "phlsys_conduit"
        self._clientVersion = 1

        self._authenticate()

    @classmethod
    def setPathToArc(cls, path):
        if not os.path.isfile(path):
            raise Exception("not a valid file: " + path)
        cls._pathToArc = path

    def _authenticate(self):
        token = str(int(time.time()))
        messageDict = {
            "user": self._username,
            "host": self._conduitUri,
            "client": self._client,
            "clientVersion": self._clientVersion,
            "authToken": token,
            "authSignature": self._generate_hash(token),
        }

        response = self._communicate("conduit.connect", messageDict)
        result = response["result"]

        self._conduit = {
            'sessionKey': result["sessionKey"],
            'connectionID': result["connectionID"],
        }

        if self._actAsUser:
            self._conduit["actAsUser"] = self._actAsUser

    def _generate_hash(self, token):
        return hashlib.sha1(token + self._certificate).hexdigest()

    def _communicate(self, method, messageDict):
        url = urlparse.urlparse(self._conduitUri)

        if url.scheme == 'https':
            conn = httplib.HTTPSConnection(url.netloc, timeout=self._timeout)
        else:
            conn = httplib.HTTPConnection(url.netloc, timeout=self._timeout)

        path = url.path + method

        headers = {
            'User-Agent': 'python-phabricator/%s' % str(self._clientVersion),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        params = json.dumps(messageDict)

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
        errorMessage = response["error_info"]
        result = response["result"]
        if error:
            raise ConduitException(
                method=method,
                error=error,
                errormsg=errorMessage,
                result=result,
                obj=param_dict,
                uri=self._conduitUri,
                actAsUser=self._actAsUser)

        return result

    def ping(self):
        return self.call("conduit.ping")


class TestConduit(unittest.TestCase):

    def setUp(self):
        self.conduit = Conduit(Conduit.testUri)

    def testCanPing(self):
        self.conduit.ping()
        self.conduit.call("differential.query")

        # TODO: test re-authentication when the token expires
        # TODO: need to test something that requires authentication


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
