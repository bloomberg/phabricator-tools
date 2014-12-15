"""Git callable that maintains a cache of refs for efficient querying."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgitx_refcache
#
# Public Classes:
#   Repo
#    .hash_ref_pairs
#    .peek_hash_ref_pairs
#    .set_hash_ref_pairs
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlgit_showref


class Repo(object):

    """Git callable that maintains a cache of refs for efficient querying."""

    def __init__(self, repo):
        """Initialise the repo to pass on calls to 'repo'."""
        super(Repo, self).__init__()
        self._repo = repo
        self._hash_ref_pairs = None

    @property
    def hash_ref_pairs(self):
        """Return a list of (sha1, name) tuples from the repo's list of refs.

        :returns: a list of (sha1, name)

        """
        if self._hash_ref_pairs is None:
            self._hash_ref_pairs = phlgit_showref.hash_ref_pairs(self._repo)
        return self._hash_ref_pairs

    def peek_hash_ref_pairs(self):
        """Return the current cached list of (sha1, name) tuples or None.

        Don't attempt to update the cache if it's stale, just return the
        current state as it is.

        This is useful if trying to persist the state in some way.

        :repo: a callable supporting git commands, e.g. repo("status")
        :returns: a list of (sha1, name)

        """
        return self._hash_ref_pairs

    def set_hash_ref_pairs(self, hash_ref_pairs):
        """Update the cached (sha1, name) tuples with the supplied list.

        This is useful if the client knows more about the state on disk in
        certain circumstances. e.g. updating with results from another process.

        :hash_ref_pairs: a list of (sha1, name)
        :returns: None

        """
        self._hash_ref_pairs = hash_ref_pairs

    def __call__(self, *args, **kwargs):
        self._hash_ref_pairs = None
        return self._repo(*args, **kwargs)

    # we don't implement this as it would be hard to guess when to invalidate
    # the cache when the client has direct access to the git directory
    #
    # @property
    # def working_dir(self):
    #     return self._repo._workingDir


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
