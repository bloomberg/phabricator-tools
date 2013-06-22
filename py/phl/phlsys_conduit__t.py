"""Test suite for phlsys_conduit"""
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

import unittest

import phldef_conduit
import phlsys_conduit


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_can_ping(self):
        test_data = phldef_conduit
        conduit = phlsys_conduit.Conduit(
            test_data.TEST_URI,
            test_data.ALICE.user,
            test_data.ALICE.certificate)
        conduit.ping()

    def test_can_list_reviews(self):
        test_data = phldef_conduit
        conduit = phlsys_conduit.Conduit(
            test_data.TEST_URI,
            test_data.ALICE.user,
            test_data.ALICE.certificate)
        conduit.call("differential.query")

    def test_can_act_as_user(self):
        test_data = phldef_conduit
        conduit = phlsys_conduit.Conduit(
            test_data.TEST_URI,
            test_data.PHAB.user,
            test_data.PHAB.certificate)
        with phlsys_conduit.act_as_user_context(conduit, test_data.ALICE.user):
            conduit.call("differential.query")

    def test_raises_on_non_auth(self):
        test_data = phldef_conduit
        self.assertRaises(
            phlsys_conduit.ConduitException,
            phlsys_conduit.Conduit,
            test_data.TEST_URI,
            "dontcreateausercalledthis",
            test_data.ALICE.certificate)

    # TODO: test re-authentication when the token expires
    # TODO: need to test something that requires authentication
    # TODO: test raises on bad instanceUri
    # TODO: test instanceUri without trailing slash


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
