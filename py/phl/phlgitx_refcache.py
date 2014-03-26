"""Git callable that maintains a cache of refs for efficient querying."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgitx_refcache
#
# Public Classes:
#   Repo
#    .hash_ref_pairs
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

        :repo: a callable supporting git commands, e.g. repo("status")
        :returns: a list of (sha1, name)

        """
        if self._hash_ref_pairs is None:
            self._hash_ref_pairs = phlgit_showref.hash_ref_pairs(self._repo)
        return self._hash_ref_pairs

    def __call__(self, *args, **kwargs):
        self._hash_ref_pairs = None
        return self._repo(*args, **kwargs)

    # we don't implement this as it would be hard to guess when to invalidate
    # the cache when the client has direct access to the git directory
    #
    # @property
    # def working_dir(self):
    #     return self._repo._workingDir


#------------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
