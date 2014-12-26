"""Naming conventions for abd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_naming
#
# Public Classes:
#   Error
#   TrackerBranch
#    .branch
#    .status
#    .description
#    .base
#    .id
#    .remote
#    .remote_base
#    .remote_branch
#    .review_name
#    .update_status
#   ReviewBranch
#    .branch
#    .description
#    .base
#    .remote
#    .remote_base
#    .remote_branch
#    .make_tracker
#
# Public Functions:
#   isStatusBad
#   isStatusBadPreReview
#   isStatusBadLand
#   get_branch_pairs
#
# Public Assignments:
#   WB_STATUS_OK
#   WB_STATUS_PREFIX_BAD
#   WB_STATUS_BAD_NAME
#   WB_STATUS_BAD_PREREVIEW
#   WB_STATUS_BAD_INREVIEW
#   WB_STATUS_BAD_LAND
#   WB_STATUS_BAD_ABANDONED
#   WB_DICT_STATUS_DESC
#   EXAMPLE_REVIEW_BRANCH_BASE
#   EXAMPLE_REVIEW_BRANCH_DESCRIPTION
#   ARCYD_BRANCH_NAMESPACE
#   TRACKING_BRANCH_PREFIX
#   RESERVED_BRANCH_NAME
#   BranchPair
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import phlgitu_ref


WB_STATUS_OK = "ok"
WB_STATUS_PREFIX_BAD = "bad_"
WB_STATUS_BAD_NAME = WB_STATUS_PREFIX_BAD + "name"
WB_STATUS_BAD_PREREVIEW = WB_STATUS_PREFIX_BAD + "prerev"
WB_STATUS_BAD_INREVIEW = WB_STATUS_PREFIX_BAD + "inrev"
WB_STATUS_BAD_LAND = WB_STATUS_PREFIX_BAD + "land"
WB_STATUS_BAD_ABANDONED = WB_STATUS_PREFIX_BAD + "abandoned"

WB_DICT_STATUS_DESC = {
    WB_STATUS_OK:            "ok",
    WB_STATUS_BAD_NAME:      "branch name is invalid",
    WB_STATUS_BAD_PREREVIEW: "didn't manage to create a review",
    WB_STATUS_BAD_INREVIEW:  "bad update during review",
    WB_STATUS_BAD_LAND:      "didn't manage to land the change",
    WB_STATUS_BAD_ABANDONED: "the review is abandoned",
}

EXAMPLE_REVIEW_BRANCH_BASE = "master"
EXAMPLE_REVIEW_BRANCH_DESCRIPTION = "mywork"

ARCYD_BRANCH_NAMESPACE = 'dev/arcyd/'
TRACKING_BRANCH_PREFIX = ARCYD_BRANCH_NAMESPACE + 'trackers/'
RESERVED_BRANCH_NAME = ARCYD_BRANCH_NAMESPACE + 'reserve'


class Error(Exception):
    pass


def isStatusBad(working_branch):
    """Return True if the status of 'working_branch' is bad.

    :working_branch: a WorkingBranch
    :returns: True if the branch is bad

    """
    return working_branch.status.startswith(WB_STATUS_PREFIX_BAD)


def isStatusBadPreReview(working_branch):
    """Return True if 'working_branch' status is WB_STATUS_BAD_PREREVIEW.

    :working_branch: a WorkingBranch
    :returns: True if the branch is in WB_STATUS_BAD_PREREVIEW

    """
    return working_branch.status == WB_STATUS_BAD_PREREVIEW


def isStatusBadLand(working_branch):
    """Return True if 'working_branch' status is WB_STATUS_BAD_PREREVIEW.

    :working_branch: a WorkingBranch
    :returns: True if the branch is in WB_STATUS_BAD_PREREVIEW

    """
    return working_branch.status == WB_STATUS_BAD_LAND


class TrackerBranch(object):

    def __init__(
            self,
            naming,
            branch,
            review_branch,
            status,
            description,
            base,
            rev_id,
            remote):
        super(TrackerBranch, self).__init__()
        self._naming = naming
        self._branch = branch
        self._status = status
        self._description = description
        self._base = base
        self._id = rev_id
        self._remote = remote
        self._remote_base = None
        self._remote_branch = None
        self._review_name = review_branch
        self._update_remotes()

    @property
    def branch(self):
        return self._branch

    @property
    def status(self):
        return self._status

    @property
    def description(self):
        return self._description

    @property
    def base(self):
        return self._base

    @property
    def id(self):
        return self._id

    @property
    def remote(self):
        return self._remote

    @property
    def remote_base(self):
        return self._remote_base

    @property
    def remote_branch(self):
        return self._remote_branch

    @property
    def review_name(self):
        return self._review_name

    def update_status(self, status):
        self._status = status
        self._branch = self._naming.make_tracker_branch_name(
            self._status, self._description, self._base, self._id)
        self._update_remotes()

    def _update_remotes(self):
        self._remote_base = phlgitu_ref.make_remote(
            self._base, self._remote)
        self._remote_branch = phlgitu_ref.make_remote(
            self._branch, self._remote)

    def __str__(self):
        return 'abdt_naming.TrackerBranch("{}")'.format(self.branch)

    __repr__ = __str__


class ReviewBranch(object):

    def __init__(
            self,
            naming,
            branch,
            description,
            base,
            remote):
        super(ReviewBranch, self).__init__()
        self._naming = naming
        self._branch = branch
        self._description = description
        self._base = base
        self._remote = remote
        self._remote_base = None
        self._remote_branch = None
        self._update_remotes()

    @property
    def branch(self):
        return self._branch

    @property
    def description(self):
        return self._description

    @property
    def base(self):
        return self._base

    @property
    def remote(self):
        return self._remote

    @property
    def remote_base(self):
        return self._remote_base

    @property
    def remote_branch(self):
        return self._remote_branch

    def make_tracker(self, status, rev_id):
        """Return a TrackerBranch based on this branch and supplied params.

        :status: the status string for the new branch
        :rev_id: the revision id string for the new branch
        :returns: a TrackerBranch

        """
        if rev_id is None:
            rev_id = "none"
        else:
            rev_id = str(rev_id)

        tracking_branch_name = self._naming.make_tracker_branch_name(
            status, self.description, self.base, rev_id)

        tracking_branch = self._naming.make_tracker_branch_from_name(
            tracking_branch_name)

        return tracking_branch

    def _update_remotes(self):
        self._remote_base = phlgitu_ref.make_remote(
            self._base, self._remote)
        self._remote_branch = phlgitu_ref.make_remote(
            self._branch, self._remote)

    def __str__(self):
        return 'abdt_naming.ReviewBranch("{}")'.format(self.branch)

    __repr__ = __str__


BranchPair = collections.namedtuple(
    "abdt_naming__BranchPair", [
        "review",
        "tracker"])


def _get_branches(branch_list, func):
    """Return a list of branches made by func() from strings in 'branch_list'.

    Strings that aren't valid working branch names are ignored, 'func' is
    expected to raise Error in this case.

    :branch_list: list of branch name strings
    :func: the branch factory funtion to use
    :returns: list of WorkingBranch

    """
    converted_branch_list = []
    for branch in branch_list:
        try:
            converted_branch_list.append(
                func(branch))
        except Error:
            pass  # ignore naming errors, we only want the valid branches
    return converted_branch_list


def get_branch_pairs(branch_list, naming):
    """Return a list of BranchPair where items in 'branch_list' are suitable.

    Note that if a review_branch or tracker_branch does not have a pair then
    the other member of the tuple is set to 'None'.

    :branch_list: a list of branch name strings to generate the pairs from
    :returns: a list of BranchPair where items in 'branch_list' are suitable

    """
    tracker_branches = _get_branches(
        branch_list, naming.make_tracker_branch_from_name)
    review_branches = _get_branches(
        branch_list, naming.make_review_branch_from_name)

    # XXX: pychecker and pyflakes don't understand dictcomps yet so do it like
    #      this instead
    name_to_tracked = dict([(b.review_name, b) for b in tracker_branches])
    name_to_review = dict([(b.branch, b) for b in review_branches])

    tracked = set(name_to_tracked.keys())
    actual = set(name_to_review.keys())

    abandoned_trackers = [name_to_tracked[b] for b in tracked - actual]
    new_reviews = [name_to_review[b] for b in actual - tracked]
    matched = actual & tracked

    res = [BranchPair(name_to_review[b], name_to_tracked[b]) for b in matched]
    res += [BranchPair(None, b) for b in abandoned_trackers]
    res += [BranchPair(b, None) for b in new_reviews]

    return res


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
