"""Generate git diffs between branches suitable for Differential reviews."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_differ
#
# Public Functions:
#   make_raw_diff
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import abdt_exception

import phlgit_diff

_LOTS_OF_DIFF_CONTEXT_LINES = 10000
_LESS_DIFF_CONTEXT_LINES = 100


def make_raw_diff(clone, base, branch, max_bytes):
    """Return a string raw diff of the changes on 'branch'.

    If the diff would exceed the _MAX_DIFF_SIZE then take measures
    to reduce the diff size by reducing the amount of context.

    Raise 'abdt_exception.LargeDiffException' if the diff could not be fit into
    'max_bytes'.

    :clone: supports 'call'
    :base: string name of the merge-base of 'branch'
    :branch: string name of the branch to diff
    :max_bytes: the maximum allowed size of the diff
    :returns: the string diff of the changes on the branch

    """
    rawDiff = phlgit_diff.raw_diff_range(
        clone, base, branch, _LOTS_OF_DIFF_CONTEXT_LINES)

    if not rawDiff:
        raise abdt_exception.AbdUserException(
            str("no difference from " + base + " to " + branch))

    # TODO: detect generated files and try less context on just those first
    # TODO: detect generated files and try no context on just those first
    # TODO: detect generated files and try excluding those first

    # if the diff is too big then regen with less context
    if len(rawDiff) >= max_bytes:
        rawDiff = phlgit_diff.raw_diff_range(
            clone, base, branch, _LESS_DIFF_CONTEXT_LINES)

    # if the diff is still too big then regen with no context
    if len(rawDiff) >= max_bytes:
        rawDiff = phlgit_diff.raw_diff_range(clone, base, branch, None)

    # if the diff is still too big then error
    if len(rawDiff) >= max_bytes:
        raise abdt_exception.LargeDiffException(
            "diff too big", len(rawDiff), max_bytes)

    # TODO: normalise any bad unicode chars and report that somehow
    # TODO: somehow report if we had to reduce the diff at all

    return rawDiff

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
