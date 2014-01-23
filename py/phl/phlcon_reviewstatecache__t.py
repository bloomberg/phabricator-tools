"""Test suite for phlcon_reviewstatecache."""
#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] ReviewStateCache passes parameters to _ReviewStateCache correctly
# [ B] ReviewStateCache asserts if set to no conduit
# [ B] ReviewStateCache asserts if queried with no conduit set
# [ B] ReviewStateCache asserts if queried before setting conduit
# [ B] _ReviewStateCache asserts if queried with no callable set
# [ B] _ReviewStateCache asserts if queried before setting callable
# [ C] _ReviewStateCache does not raise if 'refreshed' before any 'get' calls
# [ C] _ReviewStateCache does not callable when refreshing if no active queries
# [ D] _ReviewStateCache calls out to refresh queries since last refresh
# [ D] _ReviewStateCache retrieves statuses for reviews not queried before
# [ D] _ReviewStateCache does not callable when queried for cached query
# [ D] _ReviewStateCache returns correct value when retrieving cached
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_AssertIfNoQueryableSupplied
# [ C] test_C_RefreshBeforeGet
# [ D] test_D_InvalidationRules
#==============================================================================

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

        cache = phlcon_reviewstatecache.ReviewStateCache()
        cache.set_conduit(conduit)

        # assert it's in 'needs review'
        self.assertEqual(
            cache.get_status(revision_id),
            phlcon_differential.ReviewStates.needs_review)

        # change real state to 'abandoned'
        phlcon_differential.create_comment(
            conduit,
            revisionId=revision_id,
            action=phlcon_differential.Action.abandon)

        # check that the cache still reports 'needs_review'
        self.assertEqual(
            cache.get_status(revision_id),
            phlcon_differential.ReviewStates.needs_review)

        # refresh the cache
        cache.refresh_active_reviews()

        # check that the cache now reports 'abandoned'
        self.assertEqual(
            cache.get_status(revision_id),
            phlcon_differential.ReviewStates.abandoned)

    def test_B_AssertIfNoQueryableSupplied(self):

        # [  ] ReviewStateCache asserts if queried before setting conduit
        cache = phlcon_reviewstatecache.ReviewStateCache()
        self.assertRaises(
            AssertionError,
            cache.get_status,
            0)
        cache = phlcon_reviewstatecache.ReviewStateCache()
        self.assertRaises(
            AssertionError,
            cache.refresh_active_reviews)

        # [  ] ReviewStateCache asserts if set to no conduit
        cache = phlcon_reviewstatecache.ReviewStateCache()
        self.assertRaises(
            AssertionError,
            cache.set_conduit,
            None)

        # [  ] ReviewStateCache asserts if queried with no conduit set
        cache = phlcon_reviewstatecache.ReviewStateCache()
        cache.clear_conduit()
        self.assertRaises(
            AssertionError,
            cache.get_status,
            0)
        cache = phlcon_reviewstatecache.ReviewStateCache()
        cache.clear_conduit()
        self.assertRaises(
            AssertionError,
            cache.refresh_active_reviews)

        # [  ] _ReviewStateCache asserts if queried before setting callable
        cache_impl = phlcon_reviewstatecache._ReviewStateCache()
        self.assertRaises(
            AssertionError,
            cache_impl.get_status,
            0)
        cache_impl = phlcon_reviewstatecache._ReviewStateCache()
        self.assertRaises(
            AssertionError,
            cache_impl.refresh_active_reviews)

        # [  ] _ReviewStateCache asserts if queried with no callable set
        cache_impl = phlcon_reviewstatecache._ReviewStateCache()
        cache_impl.clear_revision_list_status_callable()
        self.assertRaises(
            AssertionError,
            cache_impl.get_status,
            0)
        cache_impl = phlcon_reviewstatecache._ReviewStateCache()
        cache_impl.clear_revision_list_status_callable()
        self.assertRaises(
            AssertionError,
            cache_impl.refresh_active_reviews)

    def test_C_RefreshBeforeGet(self):

        def fake_callable(revision_list):
            # [ C] _ReviewStateCache does not callable when refreshing
            #      if no active queries
            _ = revision_list  # NOQA
            raise Exception("shouldn't get here")

        # [ C] _ReviewStateCache does not raise if 'refreshed' before any 'get'
        cache_impl = phlcon_reviewstatecache._ReviewStateCache()
        cache_impl.set_revision_list_status_callable(fake_callable)
        cache_impl.refresh_active_reviews()

    def test_D_InvalidationRules(self):
        # [  ] _ReviewStateCache calls out to refresh queries since refresh
        # [  ] _ReviewStateCache retrieves statuses for reviews not queried

        revision_list = [101, 1337, 404]
        expected_queries = [[101], [1337], [404], [101, 1337, 404]]
        queried_revision_list = []

        def fake_callable(actual_revision_list):
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

        cache_impl = phlcon_reviewstatecache._ReviewStateCache()
        cache_impl.set_revision_list_status_callable(fake_callable)

        for revision in revision_list:
            cache_impl.get_status(revision)

        self.assertNotEqual(set(queried_revision_list), set(revision_list))
        cache_impl.refresh_active_reviews()
        self.assertSetEqual(set(queried_revision_list), set(revision_list))

        def raise_callable(revision_list):
            _ = revision_list  # NOQA
            raise Exception("shouldn't get here")

        cache_impl.set_revision_list_status_callable(raise_callable)

        # [ D] _ReviewStateCache does not callable if queried for cached query
        # [ D] _ReviewStateCache returns correct value when retrieving cached
        for revision in revision_list:
            result = cache_impl.get_status(revision)
            self.assertEqual(result, str(revision) + 'r')


#------------------------------------------------------------------------------
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
#------------------------------- END-OF-FILE ----------------------------------
