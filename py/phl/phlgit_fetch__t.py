"""Test suite for phlgit_fetch."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# TODO
# -----------------------------------------------------------------------------
# Tests:
# TODO
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
import unittest

import phlgit_fetch
import phlgitu_fixture


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBreathing(self):
        # pychecker won't recognise the attributes on 'f' if we create it in
        # the closing parameter list and use 'as', at least not if we create an
        # alias to the CentralisedWithTwoWorkers class
        #
        f = phlgitu_fixture.CentralisedWithTwoWorkers()
        with contextlib.closing(f):
            phlgit_fetch.prune_safe(f.w0.repo, 'origin')

    def _setupBranchBomb(self, fixture):
        """Setup a situation where fetching on w0 will fail.

        :fixture: a phlgitu_fixture.CentralisedWithTwoWorkers
        :returns: None

        """
        fixture.w1.repo('push', 'origin', 'HEAD:refs/heads/mybranch')
        fixture.w0.repo('fetch', '--prune')
        fixture.w1.repo('push', 'origin', ':refs/heads/mybranch')
        fixture.w1.repo('push', 'origin', 'HEAD:refs/heads/mybranch/bomb')

    def testBranchBomb(self):
        f = phlgitu_fixture.CentralisedWithTwoWorkers()
        with contextlib.closing(f):
            self._setupBranchBomb(f)
            phlgit_fetch.prune_safe(f.w0.repo, 'origin')
            f.w0.repo('fetch', '--prune')
            phlgit_fetch.all_prune(f.w0.repo)

    def testFetchSpec(self):
        fetchspec = ["+refs/heads/*:refs/remotes/origin/*"]
        fetchspec_nonexistant = ["+refs/nope/*:refs/heads/__private_nope/*"]

        f = phlgitu_fixture.CentralisedWithTwoWorkers()
        with contextlib.closing(f):
            phlgit_fetch.prune_safe(f.w0.repo, 'origin', [])
            phlgit_fetch.prune_safe(f.w0.repo, 'origin', fetchspec)
            phlgit_fetch.prune_safe(f.w0.repo, 'origin', fetchspec_nonexistant)


# -----------------------------------------------------------------------------
# Copyright (C) 2014-2015 Bloomberg Finance L.P.
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
