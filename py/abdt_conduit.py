"""Convenience functions for deailing with Phabricator's Conduit api."""

import phlsys_conduit
import phlcon_differential


def createEmptyRevision(conduit, author):
    empty_diff = "diff --git a/ b/"

    with phlsys_conduit.act_as_user_context(conduit, author):
        diff_id = phlcon_differential.createRawDiff(conduit, empty_diff).id
        fields = {
            "title": "empty revision",
            "testPlan": "UNTESTED",
        }
        # TODO: add support for reviewers and ccs
        # if reviewers:
        #     assert not isinstance(reviewers, types.StringTypes)
        #     fields["reviewers"] = reviewers
        # if ccs:
        #     assert not isinstance(ccs, types.StringTypes)
        #     fields["ccs"] = ccs
        revision = phlcon_differential.createRevision(conduit, diff_id, fields)
        return revision.revisionid


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
