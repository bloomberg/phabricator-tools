"""Test suite for phlcon_paste."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import phldef_conduit
import phlsys_conduit

import phlcon_paste

# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [  ] TODO
# -----------------------------------------------------------------------------
# Tests:
# TODO
# =============================================================================


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.conduit = None

    def setUp(self):
        test_data = phldef_conduit
        self.conduit = phlsys_conduit.Conduit(
            test_data.TEST_URI,
            test_data.ALICE.user,
            test_data.ALICE.certificate)

    def tearDown(self):
        pass

    def testCreatePaste(self):
        title = "paste created in tests"
        language = "text"
        content = "blah blah blah this is a paste"

        pasteResponse = phlcon_paste.create_paste(
            self.conduit, content, title, language)

        self.assertEqual(pasteResponse.content, content)
        self.assertEqual(pasteResponse.title, title)
        self.assertEqual(pasteResponse.language, language)

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
