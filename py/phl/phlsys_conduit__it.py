"""Test suite for phlsys_conduit."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# TODO
# -----------------------------------------------------------------------------
# Tests:
# TODO
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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
        conduit("differential.query")

    def test_can_act_as_user(self):
        test_data = phldef_conduit
        conduit = phlsys_conduit.Conduit(
            test_data.TEST_URI,
            test_data.PHAB.user,
            test_data.PHAB.certificate)
        with phlsys_conduit.act_as_user_context(conduit, test_data.ALICE.user):
            conduit("differential.query")

    def test_raises_on_non_auth(self):
        test_data = phldef_conduit
        self.assertRaises(
            phlsys_conduit.ConduitException,
            phlsys_conduit.Conduit,
            test_data.TEST_URI,
            "dontcreateausercalledthis",
            test_data.ALICE.certificate)

    def test_multiconduit_breathing(self):
        test_data = phldef_conduit
        conduit = phlsys_conduit.MultiConduit(
            test_data.TEST_URI,
            test_data.PHAB.user,
            test_data.PHAB.certificate)
        self.assertEqual(conduit.conduit_uri, test_data.TEST_URI)
        conduit("differential.query")
        as_user_conduit = phlsys_conduit.CallMultiConduitAsUser(conduit, 'bob')
        as_user_conduit("differential.query")

    # TODO: test re-authentication when the token expires
    # TODO: need to test something that requires authentication
    # TODO: test raises on bad instanceUri
    # TODO: test instanceUri without trailing slash


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
