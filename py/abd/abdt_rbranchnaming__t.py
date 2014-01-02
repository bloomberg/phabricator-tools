"""Test suite for abdt_rbranchnaming."""
#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
# Tests:
# [ A] XXX: test_A_Breathing
# [XA] check_XA_Breathing
# [XB] check_XB_globally_invalid_review_tracker_names
# [XC] check_XC_potentially_valid_review_tracker_names
# [XD] check_XD_valid_reviews
#==============================================================================

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
