"""Cache the results from abdt_differ."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_differresultcache
#
# Public Classes:
#   Cache
#    .get_cache
#    .set_cache
#    .checkout_make_raw_diff
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import phlgit_checkout
import phlgitu_ref

import abdt_differ


class Cache(object):

    """Cache the results from abdt_differ."""

    def __init__(self, refcache_repo):
        """Return a Cache.

        :refcache_repo: a phlgitx_refcache repository

        """
        self._diff_results = {}
        self._repo = refcache_repo

    def get_cache(self):
        """Return the cache internals for persisting.

        :returns: something suitable to supply to 'set_cache()' later

        """
        return self._diff_results

    def set_cache(self, cache):
        """Set the cache internals.

        :cache: the result of a call to get_cache()
        :returns: None

        """
        self._diff_results = cache

    def checkout_make_raw_diff(
            self, from_branch, to_branch, max_diff_size_utf8_bytes):
        """Return an abdt_differ.DiffResult of the changes on the branch.

        If the diff would exceed the pre-specified max diff size then take
        measures to reduce the diff.

        Potentially checkout onto the 'to_branch' so that changes to
        .gitattributes files will be considered.

        :from_branch: string name of the merge-base of 'branch'
        :to_branch: string name of the branch to diff
        :max_diff_size_utf8_bytes: the maximum allowed size of the diff as utf8
        :returns: the string diff of the changes on the branch

        """
        if not phlgitu_ref.is_fq(from_branch):
            raise ValueError('not fully qualifed: {}'.format(from_branch))

        if not phlgitu_ref.is_fq(to_branch):
            raise ValueError('not fully qualifed: {}'.format(from_branch))

        key = self._make_key(from_branch, to_branch, max_diff_size_utf8_bytes)
        if key in self._diff_results:
            raise self._diff_results[key]

        # checkout the 'to' branch, otherwise we won't take into account any
        # changes to .gitattributes files
        phlgit_checkout.branch(self._repo, to_branch)

        try:
            return abdt_differ.make_raw_diff(
                self._repo,
                from_branch,
                to_branch,
                max_diff_size_utf8_bytes)
        except abdt_differ.NoDiffError as e:
            self._diff_results[key] = e
            raise

    def _make_key(self, from_branch, to_branch, max_diff_size_utf8_bytes):
        from_ref, to_ref = self._refs_to_hashes(from_branch, to_branch)
        return (from_ref, to_ref, max_diff_size_utf8_bytes)

    def _refs_to_hashes(self, *ref_list):
        hash_ref_pairs = self._repo.hash_ref_pairs
        ref_to_hash = dict(((r, h) for h, r in hash_ref_pairs))
        return (ref_to_hash[ref] for ref in ref_list)


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
