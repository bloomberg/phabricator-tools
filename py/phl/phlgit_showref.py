"""Wrapper around 'git show-ref'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_showref
#
# Public Functions:
#   names
#   hash_ref_pairs
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


def names(repo):
    """Return a list of string names of the refs in the supplied repo.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: a list of string names

    """
    result = [name for sha1, name in hash_ref_pairs(repo)]
    return result


def hash_ref_pairs(repo):
    """Return a list of (sha1, name) tuples from the list of refs in 'repo'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: a list of (sha1, name)

    """
    result = [line.split() for line in repo('show-ref').splitlines()]
    return result


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
