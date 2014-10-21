"""Test suite for phlurl_watcher."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] can dump and load again from empty watcher
# [ A] can dump and load again from watcher with one element
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import phlsys_fs

import phlurl_watcher


class _MockRequesterObject(object):

    def __init__(self):
        self._request_count = 0

    def get(self, url):
        # make sure the result is different each time
        self._request_count += 1
        return (200, str(self._request_count) + url)

    def get_many(self, url_list):
        result = {}
        for url in url_list:
            result[url] = self.get(url)
        return result


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):

        with phlsys_fs.chtmpdir_context():

            requester = _MockRequesterObject()
            url = 'http://host.test'
            cache_path = 'phlurl_watcher_cache.json'

            # initialise without existing cache
            watcher_cache_wrapper = phlurl_watcher.FileCacheWatcherWrapper(
                cache_path, requester)
            watcher = watcher_cache_wrapper.watcher

            # check that we can test and consume the content change
            self.assertTrue(watcher.peek_has_url_recently_changed(url))
            self.assertTrue(watcher.peek_has_url_recently_changed(url))
            self.assertTrue(watcher.has_url_recently_changed(url))
            self.assertFalse(watcher.has_url_recently_changed(url))
            self.assertFalse(watcher.peek_has_url_recently_changed(url))

            # save and reload from the cache
            watcher_cache_wrapper.save()
            watcher_cache_wrapper = phlurl_watcher.FileCacheWatcherWrapper(
                cache_path, requester)
            watcher = watcher_cache_wrapper.watcher

            # check that the content is still considered unchanged
            self.assertFalse(watcher.has_url_recently_changed(url))
            self.assertFalse(watcher.peek_has_url_recently_changed(url))

            # check that refreshing resets the changed flags
            watcher.refresh()

            # check that we can test and consume the content change
            self.assertTrue(watcher.peek_has_url_recently_changed(url))
            self.assertTrue(watcher.peek_has_url_recently_changed(url))
            self.assertTrue(watcher.has_url_recently_changed(url))
            self.assertFalse(watcher.has_url_recently_changed(url))
            self.assertFalse(watcher.peek_has_url_recently_changed(url))

            # update the content
            watcher.refresh()

            # save and reload from the cache
            watcher_cache_wrapper.save()
            watcher_cache_wrapper = phlurl_watcher.FileCacheWatcherWrapper(
                cache_path, requester)
            watcher = watcher_cache_wrapper.watcher

            # check that we can consume the change
            self.assertTrue(watcher.peek_has_url_recently_changed(url))
            self.assertTrue(watcher.peek_has_url_recently_changed(url))
            self.assertTrue(watcher.has_url_recently_changed(url))
            self.assertFalse(watcher.has_url_recently_changed(url))
            self.assertFalse(watcher.peek_has_url_recently_changed(url))


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
