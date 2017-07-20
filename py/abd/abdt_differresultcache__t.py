"""Test suite for abdt_differresultcache."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [  ]
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
import unittest

import phlgitu_fixture
import phlgitx_refcache

import abdt_differ
import abdt_differresultcache
import abdt_exception


class _BreakableRepoUsedError(Exception):
    pass


class _BreakableRepo(object):

    def __init__(self, repo):
        super(_BreakableRepo, self).__init__()
        self._repo = repo
        self._is_enabled = True

    def __call__(self, *args):
        if self._is_enabled:
            return self._repo(*args)
        else:
            raise _BreakableRepoUsedError(str(args))

    @contextlib.contextmanager
    def disabled_context(self):
        self._is_enabled = False
        try:
            yield
        finally:
            self._is_enabled = True


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        with phlgitu_fixture.lone_worker_context() as worker:

            branch_name = 'diff_branch'

            breakable_repo = _BreakableRepo(worker.repo)
            refcache_repo = phlgitx_refcache.Repo(breakable_repo)
            differ = abdt_differresultcache.Cache(refcache_repo)

            # pylint has faulty detection here
            # pylint: disable=not-callable
            worker.repo('checkout', '-b', branch_name)
            # pylint: enable=not-callable

            def make_diff(max_bytes):
                return differ.checkout_make_raw_diff(
                    "refs/heads/master",
                    "refs/heads/{}".format(branch_name),
                    max_bytes)

            # make sure that the repo raises if used when disabled
            with self.assertRaises(_BreakableRepoUsedError):
                with breakable_repo.disabled_context():
                    with self.assertRaises(abdt_differ.NoDiffError):
                        make_diff(1)

            # An empty diff raises abdt_differ.NoDiffError
            with self.assertRaises(abdt_differ.NoDiffError):
                make_diff(1)

            # An empty diff raises abdt_differ.NoDiffError again, this time the
            # refcache_repo won't be used to do diffing so it won't need to
            # reset the cache
            with self.assertRaises(abdt_differ.NoDiffError):
                make_diff(1)

            # An empty diff raises abdt_differ.NoDiffError again
            # make sure that the repo isn't used at all, by disabling it
            with breakable_repo.disabled_context():
                with self.assertRaises(abdt_differ.NoDiffError):
                    make_diff(1)

            # the differ will detach HEAD so attach to branch again before
            # making any more commits on the branch
            # pylint has faulty detection here
            # pylint: disable=not-callable
            worker.repo('checkout', branch_name)
            # pylint: enable=not-callable

            worker.commit_new_file(
                "make a test diff", "newfile", "test content")

            # a diff within the limits passes straight through
            diff_result = make_diff(1000)
            self.assertIn("test content", diff_result.diff)

            # a diff within the limits passes straight through again
            diff_result = make_diff(1000)
            self.assertIn("test content", diff_result.diff)

            # raise if a diff cannot be reduced to the limits
            with self.assertRaises(abdt_exception.LargeDiffException):
                make_diff(1)

            # raise if a diff cannot be reduced to the limits again
            with self.assertRaises(abdt_exception.LargeDiffException):
                make_diff(1)


# -----------------------------------------------------------------------------
# Copyright (C) 2014-2017 Bloomberg Finance L.P.
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
