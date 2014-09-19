"""Cache the status of Differential revisions."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_reviewstatecache
#
# Public Classes:
#   ReviewStateCache
#    .get_state
#    .refresh_active_reviews
#
# Public Functions:
#   make_revision_list_status_callable
#
# Public Assignments:
#   ReviewState
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections

import phlcon_differential

ReviewState = collections.namedtuple(
    'phlcon_reviewstatecache__ReviewState',
    ['status', 'date_modified'])


class ReviewStateCache(object):

    def __init__(self, conduit):
        super(ReviewStateCache, self).__init__()
        self._cache = _ReviewStateCache()
        self._cache.set_revision_list_status_callable(
            make_revision_list_status_callable(
                conduit))

    def get_state(self, review_id):
        return self._cache.get_state(review_id)

    def refresh_active_reviews(self):
        self._cache.refresh_active_reviews()


def make_revision_list_status_callable(conduit):

    def revision_list_status(revision_list):
        return phlcon_differential.query(conduit, revision_list)

    return revision_list_status


class _ReviewStateCache(object):

    def __init__(self):
        super(_ReviewStateCache, self).__init__()
        self._review_to_state = {}
        self._active_reviews = set()
        self._revision_list_status_callable = None

    def _make_state(self, response):
        return ReviewState(response.status, response.dateModified)

    def get_state(self, review_id):
        assert self._revision_list_status_callable
        if review_id not in self._review_to_state:
            response = self._revision_list_status_callable([review_id])[0]
            self._review_to_state[review_id] = self._make_state(response)

        self._active_reviews.add(review_id)
        return self._review_to_state[review_id]

    def refresh_active_reviews(self):
        assert self._revision_list_status_callable
        self._review_to_state = {}
        if self._active_reviews:
            responses = self._revision_list_status_callable(
                list(self._active_reviews))
            self._review_to_state = {
                r.id: self._make_state(r) for r in responses
            }
            self._active_reviews = set()

    def set_revision_list_status_callable(self, status_callable):
        self._revision_list_status_callable = status_callable
        assert self._revision_list_status_callable

    def clear_revision_list_status_callable(self):
        self._revision_list_status_callable = None


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
