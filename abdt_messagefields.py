"""Operations involving commit messages and ParseCOmmitMessageFields."""

import phlcon_differential


def update(earlier, later):
    """Return an updated 'CommitMessageFields' based on the 'earlier' version.

    Apply the 'later' version as an update to the 'earlier' one.

    If either the earlier or later are None then the non-None one is returned.

    :earlier: a phlcon_differential.ParseCommitMessageFields
    :later: a phlcon_differential.ParseCommitMessageFields
    :returns: the updated phlcon_differential.ParseCommitMessageFields

    """
    ParseCommitMessageFields = phlcon_differential.ParseCommitMessageFields

    if earlier is None and later is not None:
        assert(isinstance(later, ParseCommitMessageFields))
        return later

    if earlier is not None and later is None:
        assert(isinstance(earlier, ParseCommitMessageFields))
        return earlier

    assert(isinstance(earlier, ParseCommitMessageFields))
    assert(isinstance(later, ParseCommitMessageFields))
    title = earlier.title
    summary = earlier.summary
    if later.summary:
        summary += "\n" + later.summary
    reviewers = set(earlier.reviewerPHIDs)
    reviewers |= set(later.reviewerPHIDs)
    reviewers = list(reviewers)
    testPlan = earlier.testPlan
    if later.testPlan:
        testPlan += "\n" + later.testPlan
    return ParseCommitMessageFields(
        title=title,
        summary=summary,
        reviewerPHIDs=reviewers,
        testPlan=testPlan)

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
