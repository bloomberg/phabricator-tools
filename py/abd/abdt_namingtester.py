"""Test suite for abdt naming convention classes."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_namingtester
#
# Public Functions:
#   check_XA_Breathing
#   check_XB_globally_invalid_review_tracker_names
#   check_XC_potentially_valid_review_tracker_names
#   check_XD_valid_reviews
#
# Public Assignments:
#   GLOBALLY_INVALID_REVIEW_TRACKER_NAMES
#   POTENTIALLY_VALID_REVIEW_NAMES
#   POTENTIALLY_VALID_TRACKER_NAMES
#   ReviewProperties
#   VALID_REVIEW_PROPERTIES
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

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
# [XA] XXX: check_XA_Breathing
# [XB] check_XB_globally_invalid_review_tracker_names
# [XC] check_XC_potentially_valid_review_tracker_names
# [XD] check_XD_valid_reviews
#==============================================================================

from __future__ import absolute_import

import collections

import phlgitu_ref

import abdt_naming


GLOBALLY_INVALID_REVIEW_TRACKER_NAMES = [
    "",
    "master",
    "develop",
    "feature/mywork",
    "releases/current",
    abdt_naming.ARCYD_BRANCH_NAMESPACE,  # without the trailing slash
    abdt_naming.TRACKING_BRANCH_PREFIX[:-1],  # without the trailing slash
    abdt_naming.RESERVED_BRANCH_NAME,
    abdt_naming.TRACKING_BRANCH_PREFIX + 'no_scheme',
    abdt_naming.TRACKING_BRANCH_PREFIX + 'no_scheme/master/mybranch/ok/99',
]

POTENTIALLY_VALID_REVIEW_NAMES = [
    "ph-review/mywork/master",
    "arcyd-review/mywork/master",
    "review/mywork",
]

POTENTIALLY_VALID_TRACKER_NAMES = [
    "dev/arcyd/ok/mywork/master/99",
    abdt_naming.TRACKING_BRANCH_PREFIX + 'my_scheme/master/mybranch/ok/99',
]


ReviewProperties = collections.namedtuple(
    'abdt_namingtester__ReviewProperties',
    ['base', 'description'])

VALID_REVIEW_PROPERTIES = [
    ReviewProperties('master', 'mywork'),
    ReviewProperties('develop', 'mywork'),
    ReviewProperties('feature/myfeature', 'mywork'),
]


def check_XA_Breathing(fixture):
    pass


def check_XB_globally_invalid_review_tracker_names(fixture, naming):
    for name in GLOBALLY_INVALID_REVIEW_TRACKER_NAMES:

        fixture.assertRaises(
            abdt_naming.Error,
            lambda: naming.make_review_branch_from_name(name))

        fixture.assertRaises(
            abdt_naming.Error,
            lambda: naming.make_tracker_branch_from_name(name))


def check_XC_potentially_valid_review_tracker_names(fixture, naming):
    for name in POTENTIALLY_VALID_REVIEW_NAMES:

        fixture.assertRaises(
            abdt_naming.Error,
            lambda: naming.make_tracker_branch_from_name(name))

    for name in POTENTIALLY_VALID_TRACKER_NAMES:

        fixture.assertRaises(
            abdt_naming.Error,
            lambda: naming.make_review_branch_from_name(name))


def _check_tracker_params(
        fixture, tracker, review, status, review_id):
    fixture.assertEqual(review.branch, tracker.review_name)
    fixture.assertEqual(review.base, tracker.base)
    fixture.assertEqual(review.description, tracker.description)
    fixture.assertEqual(status, tracker.status)
    fixture.assertEqual(review_id, tracker.id)
    fixture.assertEqual(review.remote, tracker.remote)
    fixture.assertEqual(
        phlgitu_ref.make_remote(tracker.base, tracker.remote),
        tracker.remote_base)
    fixture.assertEqual(
        phlgitu_ref.make_remote(tracker.branch, tracker.remote),
        tracker.remote_branch)


def _check_tracker(
        fixture, naming, tracker, review, status, review_id):
    _check_tracker_params(fixture, tracker, review, status, review_id)
    tracker = naming.make_tracker_branch_from_name(tracker.branch)
    _check_tracker_params(fixture, tracker, review, status, review_id)


def check_XD_valid_reviews(fixture, naming, names_to_properties):
    """Check that the supplied names make reviews with the supplied properties.

    :fixture: supports the unittest.TestCase assertions
    :naming: the naming convention object under test
    :names_to_properties: a dict of branch name string to ReviewProperties
    :returns: None

    """
    remote = 'origin'

    tracker_names = []

    for name, properties in names_to_properties.iteritems():
        print properties
        review = naming.make_review_branch_from_name(name)

        # [XD] ReviewBranches created by the scheme have the expected
        #      attributes

        fixture.assertEqual(name, review.branch)
        fixture.assertEqual(properties.base, review.base)
        fixture.assertEqual(properties.description, review.description)
        fixture.assertEqual(remote, review.remote)
        fixture.assertEqual(
            phlgitu_ref.make_remote(properties.base, review.remote),
            review.remote_base)
        fixture.assertEqual(
            phlgitu_ref.make_remote(name, review.remote),
            review.remote_branch)

        # [XD] ReviewBranches created by the scheme can create expected
        #      TrackerBranches

        # [XD] TrackerBranches created by the scheme have the expected
        #      attributes

        tracker = review.make_tracker(
            abdt_naming.WB_STATUS_BAD_PREREVIEW, None)
        _check_tracker(
            fixture,
            naming,
            tracker,
            review,
            abdt_naming.WB_STATUS_BAD_PREREVIEW,
            "none")
        tracker_names.append(tracker.branch)

        tracker = review.make_tracker(abdt_naming.WB_STATUS_OK, 99)
        _check_tracker(
            fixture, naming, tracker, review, abdt_naming.WB_STATUS_OK, '99')
        tracker_names.append(tracker.branch)

        tracker = review.make_tracker(abdt_naming.WB_STATUS_BAD_INREVIEW, 1)
        _check_tracker(
            fixture,
            naming,
            tracker,
            review,
            abdt_naming.WB_STATUS_BAD_INREVIEW,
            '1')
        tracker_names.append(tracker.branch)

    # [XD] there is a 1-1 relationship between tracker params and tracker names
    fixture.assertEqual(
        len(tracker_names),
        len(set(tracker_names)))


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
