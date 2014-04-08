"""Cache the status of Differential revisions."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_reviewstatecache
#
# Public Classes:
#   ReviewStateCache
#    .get_status
#    .get_date_modified
#    .refresh_active_reviews
#    .set_conduit
#    .clear_conduit
#
# Public Functions:
#   make_revision_list_status_callable
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections

import phlcon_differential


class ReviewStateCache(object):

    def __init__(self):
        super(ReviewStateCache, self).__init__()
        self._cache = _ReviewStateCache()

    def get_status(self, review_id):
        return self._cache.get_status(review_id)

    def get_date_modified(self, review_id):
        return self._cache.get_date_modified(review_id)

    def refresh_active_reviews(self):
        self._cache.refresh_active_reviews()

    def set_conduit(self, conduit):
        assert conduit
        self._cache.set_revision_list_status_callable(
            make_revision_list_status_callable(
                conduit))

    def clear_conduit(self):
        self._cache.clear_revision_list_status_callable()


def make_revision_list_status_callable(conduit):

    def revision_list_status(revision_list):
        return phlcon_differential.query(conduit, revision_list)

    return revision_list_status


_ReviewState = collections.namedtuple(
    'phlcon_reviewstatecache__ReviewState',
    ['status', 'date_modified'])


class _ReviewStateCache(object):

    def __init__(self):
        super(_ReviewStateCache, self).__init__()
        self._review_to_state = {}
        self._active_reviews = set()
        self._revision_list_status_callable = None

    def _make_state(self, response):
        return _ReviewState(response.status, response.dateModified)

    def _get_state(self, review_id):
        assert self._revision_list_status_callable
        if review_id not in self._review_to_state:
            response = self._revision_list_status_callable([review_id])[0]
            self._review_to_state[review_id] = self._make_state(response)

        self._active_reviews.add(review_id)
        return self._review_to_state[review_id]

    def get_status(self, review_id):
        return self._get_state(review_id).status

    def get_date_modified(self, review_id):
        return self._get_state(review_id).date_modified

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
