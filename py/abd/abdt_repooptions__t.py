"""Test suite for abdt_repooptions."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] can serialize and deserialize a default abdt_repooptions.Data
# [ B] can override one data with another, only applying non-None attributes
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_Combine
# =============================================================================

from __future__ import absolute_import

import unittest

import abdt_repooptions


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        data = abdt_repooptions.Data()
        data_json = abdt_repooptions.json_from_data(data)
        data2 = abdt_repooptions.data_from_json(data_json)
        self.assertEqual(data, data2)

    def test_B_Combine(self):
        # can override one data with another, only applying non-None attributes
        data1 = abdt_repooptions.Data()
        data1.description = '1'
        data1.branch_url_format = 'format'
        data1.admin_emails = ['data1_admin']
        data2 = abdt_repooptions.Data()
        data2.description = '2'
        data2.admin_emails = ['data2_admin1', 'data2_admin2']
        all_emails_set = set(data1.admin_emails + data2.admin_emails)

        data1_2 = abdt_repooptions.merge_data_objects(data1, data2)
        self.assertEqual(data1_2.description, data2.description)
        self.assertEqual(data1_2.branch_url_format, data1.branch_url_format)
        self.assertSetEqual(set(data1_2.admin_emails), all_emails_set)

        data2_1 = abdt_repooptions.merge_data_objects(data2, data1)
        self.assertEqual(data2_1.description, data1.description)
        self.assertEqual(data2_1.branch_url_format, data1.branch_url_format)
        self.assertSetEqual(set(data1_2.admin_emails), all_emails_set)


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
