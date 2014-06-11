"""Watch URLs for recent changes, batch updates and re-use connections."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlurl_watcher
#
# Public Classes:
#   Watcher
#    .peek_has_url_recently_changed
#    .has_url_recently_changed
#    .refresh
#    .load
#    .dump
#   FileCacheWatcherWrapper
#    .watcher
#    .save
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections
import hashlib
import json
import os

import phlurl_request


_HashHexdigestHasChanged = collections.namedtuple(
    'phlurl_watcher__HashValueHasChanged',
    ['hash_hexdigest', 'has_changed'])


class Watcher(object):

    def __init__(self, requester_object=None):
        super(Watcher, self).__init__()
        self._results = {}
        self._requester_object = requester_object
        if self._requester_object is None:
            self._requester_object = phlurl_request

    def _request_and_set_has_changed(self, url, has_changed):
        content = self._requester_object.get(url)
        # pylint: disable=E1101
        self._results[url] = _HashHexdigestHasChanged(
            hashlib.sha1(content).hexdigest(), has_changed)
        # pylint: enable=E1101
        return True

    def peek_has_url_recently_changed(self, url):
        """Return True if the url has recently changed, otherwise False.

        Note that this call does not consume the 'newness' of the url's
        content.

        """
        if url in self._results:
            return self._results[url].has_changed

        # this is the first query for this url
        self._request_and_set_has_changed(url, has_changed=True)
        return True

    def has_url_recently_changed(self, url):
        """Return True if the url has recently changed, otherwise False.

        Note that the next calls to this method will return False, as the
        'newness' of the url's content will be considered as 'consumed'.

        The 'newness' status will be updated during the next call to 'refresh'.

        """
        if url in self._results:
            old_result = self._results[url].has_changed
            if old_result:
                hash_hexdigest = self._results[url].hash_hexdigest
                self._results[url] = _HashHexdigestHasChanged(
                    hash_hexdigest, False)
            return old_result

        # this is the first query for this url
        self._request_and_set_has_changed(url, has_changed=False)
        return True

    def refresh(self):
        # XXX: it's safe to refresh multiple times - the 'has changed' flag
        #      is only consumed on 'has_url_recently_changed'
        url_contents = self._requester_object.get_many(self._results.keys())
        for url, contents in url_contents.iteritems():
            old_result = self._results[url]

            # Note that hash objects can't be compared directly so we much
            # first convert them to a representation that can be compared, in
            # this case we've chosen the hexdigest.
            #
            # Note that if you do try to compare hash objects then it seems to
            # do the 'is' comparison rather than 'is equal to'
            #
            # pylint: disable=E1101
            new_hash = hashlib.sha1(contents).hexdigest()
            # pylint: enable=E1101
            old_hash = old_result.hash_hexdigest
            has_changed = old_result.has_changed or (new_hash != old_hash)

            self._results[url] = _HashHexdigestHasChanged(
                new_hash, has_changed)

    def load(self, f):
        """Load data from the supplied file pointer, overwriting existing data.

        :f: a text file pointer to load from
        :returns: None

        """
        results = json.load(f)
        self._results = dict(
            (k, _HashHexdigestHasChanged(*v)) for k, v in results.iteritems())

    def dump(self, f):
        """Dump data to the supplied file pointer.

        :f: a text file pointer to dump to
        :returns: None

        """
        json.dump(self._results, f)


class FileCacheWatcherWrapper(object):

    def __init__(self, filename, requester_object=None):
        self._filename = os.path.abspath(filename)
        self._watcher = Watcher(requester_object)

        # load the url watcher cache (if any)
        if os.path.isfile(self._filename):
            with open(self._filename) as f:
                self._watcher.load(f)
        else:
            # try to fail early by creating a cache if it doesn't exist already
            self.save()

    @property
    def watcher(self):
        return self._watcher

    def save(self):
        with open(self._filename, 'w') as f:
            self._watcher.dump(f)


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
