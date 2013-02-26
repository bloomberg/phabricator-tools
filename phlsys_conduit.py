"""Wrapper to call Phabricator's Conduit API"""

import json
import os
import unittest

import phlsys_subprocess


class ConduitException(Exception):
    def __init__(self, method, error, errormsg, response, obj, uri, actAsUser):
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
            "response: '" + str(response) + "'\n" +
            "object: '" + str(obj) + "'\n" +
            "uri: '" + str(uri) + "'\n" +
            "actAsUser: '" + str(uri) + "'\n")
        super(ConduitException, self).__init__(message)
        self.method = method
        self.error = error
        self.errormsg = errormsg
        self.response = response
        self.obj = obj
        self.uri = uri
        self.actAsUser = actAsUser


class Conduit():

    # XXX: we rely on arcanist to talk to Conduit.. for now
    _pathToArc = "arc"

    # TODO: determine this by some 'official' means, perhaps
    #       use test.phab.dev.bloomberg.com for example
    testUri = "https://lo50f-04-087a.corp.bloomberg.com"

    def __init__(self, conduitUri, actAsUser=None):
        self._conduitUri = conduitUri
        self._actAsUser = actAsUser

    @classmethod
    def setPathToArc(cls, path):
        if not os.path.isfile(path):
            raise Exception("not a valid file: " + path)
        cls._pathToArc = path

    def call(self, method, objIn):
        jsonIn = json.dumps(objIn)
        args = [Conduit._pathToArc, 'call-conduit']
        args.extend(('--conduit-uri', self._conduitUri))
        if self._actAsUser:
            args.extend(('--conduit-act-as-user', self._actAsUser))
        args.append(method)
        # TODO: catch subprocess exceptions here
        result = phlsys_subprocess.run(*args, stdin=jsonIn)
        jsonOut = json.loads(result.stdout)
        error = jsonOut["error"]
        errorMessage = jsonOut["errorMessage"]
        response = jsonOut["response"]
        if error:
            raise ConduitException(
                method=method,
                error=error,
                errormsg=errorMessage,
                response=response,
                obj=objIn,
                uri=self._conduitUri,
                actAsUser=self._actAsUser)
                # "phlsys_conduit.Conduit\n" +
                # "method: '" + str(method) + "'\n" +
                # "error: '" + str(error) + "'\n" +
                # "message: '" + str(errorMessage) + "'\n" +
                # "response: '" + str(response) + "'\n" +
                # "object: '" + str(objIn) + "'\n" +
                # "uri: '" + str(self._conduitUri) + "'\n" +
                # "actAsUser: '" + str(self._actAsUser) + "'\n")
        return response

    def ping(self):
        return self.call("conduit.ping", {})


class TestConduit(unittest.TestCase):

    def setUp(self):
        self.conduit = Conduit(Conduit.testUri)
        user = "lilit"
        self.conduitAsUser = Conduit(Conduit.testUri, user)

    def testCanPing(self):
        self.conduit.ping()
        self.conduitAsUser.ping()


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
