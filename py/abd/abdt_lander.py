"""Callables for re-integrating branches upstream.

This component provides a number of 'landers', which will re-integrate a
feature branch back into the current branch, which is assumed to be upstream.

In other words, the 'landers' land a supplied branch on the current branch.

Landers have the interface:
    def lander(repo, feature, author_name, author_email, message)

On success the lander will return a string summary of the landing operation
for a human to review.

If the lander fails to land then it will raise a LanderException with details
of the failure.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_lander
#
# Public Classes:
#   LanderException
#
# Public Functions:
#   squash
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlgit_merge


class LanderException(Exception):

    def __init__(self, description):
        super(LanderException, self).__init__(description)


def squash(repo, source, author_name, author_email, message):
    """Return the string output of squashing 'source' into current branch."""
    try:
        result = repo.squash_merge(
            source,
            message,
            author_name,
            author_email)
    except phlgit_merge.MergeException as e:
        raise LanderException(e)

    return result


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
