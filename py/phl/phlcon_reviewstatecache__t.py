"""Test suite for phlcon_reviewstatecache."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ C] ReviewStateCache does not raise if 'refreshed' before any 'get' calls
# [ C] ReviewStateCache does not callable when refreshing if no active queries
# [ D] ReviewStateCache calls out to refresh queries since last refresh
# [ D] ReviewStateCache retrieves statuses for reviews not queried before
# [ D] ReviewStateCache does not callable when queried for cached query
# [ D] ReviewStateCache returns correct value when retrieving cached
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ C] test_C_RefreshBeforeGet
# [ D] test_D_InvalidationRules
# =============================================================================

from __future__ import absolute_import

import collections
import unittest

import phldef_conduit
import phlsys_conduit

import phlcon_differential
import phlcon_reviewstatecache


FakeResult = collections.namedtuple(
    'phlcon_reviewstatecache__t_FakeResult',
    ['id', 'status', 'dateModified'])


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        test_data = phldef_conduit
        conduit = phlsys_conduit.Conduit(
            test_data.TEST_URI,
            test_data.PHAB.user,
            test_data.PHAB.certificate)

        revision_id = phlcon_differential.create_empty_revision(conduit)

        cache = phlcon_reviewstatecache.make_from_conduit(conduit)

        # assert it's in 'needs review'
        self.assertEqual(
            cache.get_state(revision_id).status,
            phlcon_differential.ReviewStates.needs_review)

        # change real state to 'abandoned'
        phlcon_differential.create_comment(
            conduit,
            revisionId=revision_id,
            action=phlcon_differential.Action.abandon)

        # check that the cache still reports 'needs_review'
        self.assertEqual(
            cache.get_state(revision_id).status,
            phlcon_differential.ReviewStates.needs_review)

        # refresh the cache
        cache.refresh_active_reviews()

        # check that the cache now reports 'abandoned'
        self.assertEqual(
            cache.get_state(revision_id).status,
            phlcon_differential.ReviewStates.abandoned)

    def test_C_RefreshBeforeGet(self):

        def fake_callable(revision_list):
            # [ C] ReviewStateCache does not callable when refreshing
            #      if no active queries
            _ = revision_list  # NOQA
            raise Exception("shouldn't get here")

        # [ C] ReviewStateCache does not raise if 'refreshed' before any 'get'
        cache_impl = phlcon_reviewstatecache.ReviewStateCache(fake_callable)
        cache_impl.refresh_active_reviews()

    def test_D_InvalidationRules(self):
        # [  ] ReviewStateCache calls out to refresh queries since refresh
        # [  ] ReviewStateCache retrieves statuses for reviews not queried

        revision_list = [101, 1337, 404]
        expected_queries = [[101], [1337], [404], [101, 1337, 404]]
        queried_revision_list = []
        callable_should_raise = False

        def fake_callable(actual_revision_list):

            if callable_should_raise:
                raise Exception("shouldn't get here")

            # N.B. we have to assign to the slice as we're in a nested func
            #      and otherwise we won't be referring to the same data
            #      in Python 3 we can do better with nonlocal
            queried_revision_list[:] = actual_revision_list
            print queried_revision_list

            next_expected_query = expected_queries[0]
            self.assertSetEqual(
                set(queried_revision_list),
                set(next_expected_query))

            # erase the head of the expected queries list, moving on the next
            # N.B. we have to assign to the slice as we're in a nested func
            #      and otherwise we won't be referring to the same data
            #      in Python 3 we can do better with nonlocal
            expected_queries[:] = expected_queries[1:]

            return [
                FakeResult(r, str(r) + 'r', str(r) + 'd')
                for r in actual_revision_list
            ]

        cache_impl = phlcon_reviewstatecache.ReviewStateCache(fake_callable)

        # exercise getting the state
        for revision in revision_list:
            _ = cache_impl.get_state(revision).status  # NOQA

        self.assertNotEqual(set(queried_revision_list), set(revision_list))
        cache_impl.refresh_active_reviews()
        self.assertSetEqual(set(queried_revision_list), set(revision_list))

        callable_should_raise = True

        # [ D] ReviewStateCache does not callable if queried for cached query
        # [ D] ReviewStateCache returns correct value when retrieving cached
        for revision in revision_list:
            result = cache_impl.get_state(revision).status
            self.assertEqual(result, str(revision) + 'r')


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
