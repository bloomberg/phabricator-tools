"""Test suite for abdt_conduitmock."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] public interface of mock matches abdt_conduit.Conduit
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_InterfaceMatchesRealConduit
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import phlsys_compiface

import abdt_conduit
import abdt_conduitmock


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        pass

    def test_B_InterfaceMatchesRealConduit(self):
        self.assertTrue(
            phlsys_compiface.check_public_ifaces_match(
                abdt_conduit.Conduit,
                abdt_conduitmock.ConduitMock))


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
