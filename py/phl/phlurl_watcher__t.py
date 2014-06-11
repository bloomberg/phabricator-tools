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

import unittest

import phlsys_fs

import phlurl_watcher


class _MockRequesterObject(object):

    def __init__(self):
        self._request_count = 0

    def get(self, url):
        # make sure the result is different each time
        self._request_count += 1
        return str(self._request_count) + url

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
