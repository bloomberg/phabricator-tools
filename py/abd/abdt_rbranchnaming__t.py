"""Test suite for abdt_rbranchnaming."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [XB] review names that are globally known to be bad are not accepted
# [XB] tracker names that are globally known to be bad are not accepted
# [XC] names that are known to be potential reviews aren't accepted as trackers
# [XC] names that are known to be potential trackers aren't accepted as reviews
# [XD] ReviewBranches created by the scheme have the expected attributes
# [XD] ReviewBranches created by the scheme can create expected TrackerBranches
# [XD] TrackerBranches created by the scheme have the expected attributes
# [XD] there is a 1-1 relationship between tracker params and tracker names
# -----------------------------------------------------------------------------
# Tests:
# [ A] XXX: test_A_Breathing
# [XA] check_XA_Breathing
# [XB] check_XB_globally_invalid_review_tracker_names
# [XC] check_XC_potentially_valid_review_tracker_names
# [XD] check_XD_valid_reviews
# =============================================================================

from __future__ import absolute_import

import unittest

import abdt_namingtester
import abdt_rbranchnaming


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_naming(self):
        return abdt_rbranchnaming.Naming()

    def test_A_Breathing(self):
        pass

    def test_XA_Breathing(self):
        abdt_namingtester.check_XA_Breathing(self)

    def test_XB_globally_invalid_review_tracker_names(self):
        abdt_namingtester.check_XB_globally_invalid_review_tracker_names(
            self, self.make_naming())

    def test_XC_potentially_valid_review_tracker_names(self):
        abdt_namingtester.check_XC_potentially_valid_review_tracker_names(
            self, self.make_naming())

    def test_XD_valid_reviews(self):
        names_to_properties = {}

        for properties in abdt_namingtester.VALID_REVIEW_PROPERTIES:

            name = 'r/{base}/{description}'.format(
                description=properties.description,
                base=properties.base)

            assert name not in names_to_properties
            names_to_properties[name] = properties

        abdt_namingtester.check_XD_valid_reviews(
            self, self.make_naming(), names_to_properties)


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
