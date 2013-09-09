"""Wrapper around 'git diff'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_diff
#
# Public Functions:
#   raw_diff_range_to_here
#   raw_diff_range
#   parse_filenames_from_raw_diff
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import re


def raw_diff_range_to_here(clone, start):
    return clone.call("diff", start + "...", "-M")


def raw_diff_range(clone, base, new, context_lines=None):
    """Return a raw diff from the history on 'new' that is not on 'base'.

    Note that commits that are cherry-picked from new to old will still appear
    in the diff, this function operates using the commit graph only.

    Raise if git returns a non-zero exit code.

    :clone: the clone to operate on
    :base: the base branch
    :new: the branch with new commits
    :returns: a string of the raw diff

    """
    args = [
        "diff",
        base + "..." + new,
        "-M",  # automatically detect moves/renames
    ]

    if context_lines:
        args.append("--unified=" + str(context_lines))

    result = clone.call(*args)
    return result


def parse_filenames_from_raw_diff(diff):
    matches = re.findall(
        "^diff --git a/(.*) b/(.*)$",
        diff,
        flags=re.MULTILINE)
    if matches:
        names = zip(*matches)
        if len(names) != 2:
            raise Exception(
                "files aren't pairs in diff: " +
                diff + str(names))
        # get a set of unique names from the pairs
        unames = []
        unames.extend(names[0])
        unames.extend(names[1])
        unames = set(unames)
        return unames


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
