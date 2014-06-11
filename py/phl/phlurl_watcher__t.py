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


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):

        # N.B. We have to assign to an array as we're in a nested func
        #      and otherwise we won't be referring to the same data.
        #      In Python 3 we can do better with 'nonlocal'
        request_count = [0]

        def request_func(url):
            # make sure the result is different each time
            request_count[0] += 1
            return str(request_count[0]) + url

        watcher = phlurl_watcher.Watcher(request_func)

        with phlsys_fs.chtmpdir_context():

            with open('data', 'w') as f:
                watcher.dump(f)
            with open('data') as f:
                watcher.load(f)

            url = 'http://z.com'

            self.assertTrue(watcher.peek_has_url_recently_changed(url))
            self.assertTrue(watcher.peek_has_url_recently_changed(url))
            self.assertTrue(watcher.has_url_recently_changed(url))
            self.assertFalse(watcher.has_url_recently_changed(url))
            self.assertFalse(watcher.peek_has_url_recently_changed(url))

            with open('data', 'w') as f:
                watcher.dump(f)
            with open('data') as f:
                watcher.load(f)

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
