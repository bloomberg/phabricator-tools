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
# ------------------------------ END-OF-FILE ----------------------------------
