"""Utilities for working with git refs."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgitu_ref
#
# Public Functions:
#   make_remote
#   make_local
#   parse_ref_hash
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


def make_remote(ref, remote):
    """Return a Git reference based on a local name and a remote name.

    Usage example:
        >>> make_remote("mywork", "origin")
        'refs/remotes/origin/mywork'

        >>> make_remote("mywork", "github")
        'refs/remotes/github/mywork'

    """
    return "refs/remotes/" + remote + "/" + ref


def make_local(ref):
    """Return a fully qualified Git reference based on a local name.

    Usage example:
        >>> make_local("mywork")
        'refs/heads/mywork'

    """
    # TODO: check that it isn't already fully qualified
    return "refs/heads/" + ref


def parse_ref_hash(clone, ref):
    """Return string of the ref's commit hash if valid, else None.

    :clone: supports call()
    :ref: the reference to parse
    :returns: string of the ref's commit hash if valid, else None.

    """
    commit = clone.call("rev-parse", "--revs-only", ref)
    return commit if commit else None

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
