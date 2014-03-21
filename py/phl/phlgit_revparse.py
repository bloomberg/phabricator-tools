"""Wrapper around 'git rev-parse'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_revparse
#
# Public Classes:
#   Error
#
# Public Functions:
#   get_sha1_or_none
#   get_sha1
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


class Error(Exception):
    pass


def get_sha1_or_none(repo, ref):
    """Return string of the ref's commit hash if valid, else None.

    :repo: supports call()
    :ref: string of the reference to parse
    :returns: string of the ref's commit hash if valid, else None.

    """
    commit = repo("rev-parse", "--revs-only", ref).strip()
    return commit if commit else None


def get_sha1(repo, ref):
    """Return string of the ref's commit hash.

    Raise if the ref is invalid.

    :repo: supports call()
    :ref: string of the reference to parse
    :returns: string of the ref's commit hash

    """
    commit = get_sha1_or_none(repo, ref)
    if commit is None:
        raise Error("ref '{}' is invalid.".format(ref))
    return commit


#------------------------------------------------------------------------------
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
#------------------------------- END-OF-FILE ----------------------------------
