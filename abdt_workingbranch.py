import abdt_naming
import phlgit_push
import phlgitu_ref
import abdt_gittypes


def pushBadInReview(gitContext, review_branch, working_branch):
    pushStatus(
        gitContext,
        review_branch,
        working_branch,
        abdt_naming.WB_STATUS_BAD_INREVIEW)


def pushStatus(gitContext, review_branch, working_branch, status):
    clone = gitContext.clone
    remote = gitContext.remote
    old_branch = working_branch.branch

    working_branch = abdt_gittypes.makeWorkingBranchWithStatus(
        working_branch, status)

    new_branch = working_branch.branch
    if old_branch == new_branch:
        phlgit_push.pushAsymmetricalForce(
            clone,
            review_branch.remote_branch,
            phlgitu_ref.makeLocal(new_branch),
            remote)
    else:
        phlgit_push.moveAsymmetrical(
            clone,
            review_branch.remote_branch,
            phlgitu_ref.makeLocal(old_branch),
            phlgitu_ref.makeLocal(new_branch),
            remote)


def pushBadPreReview(gitContext, review_branch):
    working_branch_name = abdt_naming.makeWorkingBranchName(
        abdt_naming.WB_STATUS_BAD_PREREVIEW,
        review_branch.description, review_branch.base, "none")
    phlgit_push.pushAsymmetrical(
        gitContext.clone,
        phlgitu_ref.makeRemote(
            review_branch.branch, gitContext.remote),
        phlgitu_ref.makeLocal(working_branch_name),
        gitContext.remote)


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
