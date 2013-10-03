"""Watch URLs for recent changes, batch updates and re-use connections."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlurl_watcher
#
# Public Classes:
#   Watcher
#    .has_url_recently_changed
#    .refresh
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections
import hashlib

import phlurl_request


_HashValueHasChanged = collections.namedtuple(
    'phlurl_watcher__HashValueHasChanged',
    ['hash_value', 'has_changed'])


class Watcher(object):

    def __init__(self):
        super(Watcher, self).__init__()
        self._results = {}

    def has_url_recently_changed(self, url):
        if url in self._results:
            old_result = self._results[url].has_changed
            if old_result:
                hash_value = self._results[url].hash_value
                self._results[url] = _HashValueHasChanged(hash_value, False)
            return old_result
        content = phlurl_request.get(url)
        self._results[url] = _HashValueHasChanged(hashlib.sha1(content), False)
        return True

    def refresh(self):
        # XXX: it's safe to refresh multiple times - the 'has changed' flag
        #      is only consumed on 'has_url_recently_changed'
        url_contents = phlurl_request.get_many(self._results.keys())
        for url, contents in url_contents.iteritems():
            old_result = self._results[url]
            new_hash = hashlib.sha1(contents)
            old_hash = old_result.hash_value
            has_changed = old_result.has_changed or (new_hash != old_hash)
            self._results[url] = _HashValueHasChanged(new_hash, has_changed)


#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
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
