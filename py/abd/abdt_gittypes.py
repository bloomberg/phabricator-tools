"""Define useful aggregates for interacting with git without passing alot."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
#
# Public Functions:
#   makeWorkingBranchWithStatus
#   makeGitWorkingBranch
#   makeGitWorkingBranchFromParts
#   makeGitReviewBranch
#
# Public Assignments:
#   GitReviewBranch
#   GitWorkingBranch
#   GitContext
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import collections

import phlgitu_ref

import abdt_naming


GitReviewBranch = collections.namedtuple(
    "abdcmd_default__GitReviewBranch", [
        "branch",
        "description",
        "base",
        "remote",
        "remote_base",
        "remote_branch"])

GitWorkingBranch = collections.namedtuple(
    "abdcmd_default__GitWorkingBranch", [
        "branch",
        "status",
        "description",
        "base",
        "id",
        "remote",
        "remote_base",
        "remote_branch"])

GitContext = collections.namedtuple(
    "abdcmd_default__GitContext", [
        "clone",
        "remote",
        "branches"])


def makeWorkingBranchWithStatus(working_branch, status):
    """Return an abdcmd_default__GitWorkingBranch based on branch and status.

    :working_branch: an abdcmd_default__GitWorkingBranch to base on
    :status: the new string status
    :returns: an abdcmd_default__GitWorkingBranch

    """
    remote = working_branch.remote
    working_branch = abdt_naming.makeWorkingBranchName(
        base=working_branch.base,
        status=status,
        description=working_branch.description,
        review_id=working_branch.id)
    working_branch = abdt_naming.makeWorkingBranchFromName(working_branch)
    working_branch = makeGitWorkingBranch(working_branch, remote)
    return working_branch


def makeGitWorkingBranch(working_branch, remote):
    """Return GitWorkingBranch based on a abdt_naming.WorkingBranch and remote.

    :working_branch: an abdt_naming.WorkingBranch to base this on
    :remote: the name of the remote to use
    :returns: a GitWorkingBranch

    """
    makeRemote = phlgitu_ref.makeRemote
    return GitWorkingBranch(
        branch=working_branch.branch,
        status=working_branch.status,
        description=working_branch.description,
        base=working_branch.base,
        id=working_branch.id,
        remote=remote,
        remote_base=makeRemote(working_branch.base, remote),
        remote_branch=makeRemote(working_branch.branch, remote))


def makeGitWorkingBranchFromParts(
        status, description, base, review_id, remote):
    """Return a GitReviewBranch based on the supplied parts."""
    working_branch = abdt_naming.makeWorkingBranchName(
        base=base,
        status=status,
        description=description,
        review_id=review_id)
    working_branch = abdt_naming.makeWorkingBranchFromName(working_branch)
    working_branch = makeGitWorkingBranch(working_branch, remote)
    return working_branch


def makeGitReviewBranch(review_branch, remote):
    """Return a GitReviewBranch based on a abdt_naming.ReviewBranch and remote.

    :review_branch: an abdt_naming.ReviewBranch to base this on
    :remote: the name of the remote to use
    :returns: a GitReviewBranch

    """
    makeRemote = phlgitu_ref.makeRemote
    return GitReviewBranch(
        branch=review_branch.branch,
        description=review_branch.description,
        base=review_branch.base,
        remote=remote,
        remote_base=makeRemote(review_branch.base, remote),
        remote_branch=makeRemote(review_branch.branch, remote))


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
