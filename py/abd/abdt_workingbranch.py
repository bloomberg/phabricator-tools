"""Git operations on working branches."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_workingbranch
#
# Public Functions:
#   push_bad_pre_review
#   push_ok_new_in_review
#   push_bad_new_in_review
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlgit_push
import phlgitu_ref

import abdt_naming


def push_bad_pre_review(clone, review_branch):
    return _push_new_status_branch(
        clone,
        review_branch,
        abdt_naming.WB_STATUS_BAD_PREREVIEW,
        None)


def push_ok_new_in_review(clone, review_branch, revision_id):
    return _push_new_status_branch(
        clone,
        review_branch,
        abdt_naming.WB_STATUS_OK,
        revision_id)


def push_bad_new_in_review(clone, review_branch, revision_id):
    return _push_new_status_branch(
        clone,
        review_branch,
        abdt_naming.WB_STATUS_BAD_INREVIEW,
        revision_id)


def _push_new_status_branch(clone, review_branch, status, revision_id):
    if revision_id is None:
        revision_id = "none"
    else:
        revision_id = str(revision_id)

    naming = abdt_naming.ClassicNaming()

    working_branch_name = naming.make_tracker_branch_name(
        status,
        review_branch.description,
        review_branch.base,
        revision_id)

    working_branch = naming.make_tracker_branch_from_name(working_branch_name)

    phlgit_push.push_asymmetrical_force(
        clone,
        review_branch.remote_branch,
        phlgitu_ref.make_local(working_branch.branch),
        working_branch.remote)

    return working_branch


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
