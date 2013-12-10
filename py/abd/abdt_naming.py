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
#   ClassicNaming
#    .make_tracker_branch_from_name
#    .make_tracker_branch_name
#    .make_review_branch_from_name
#    .make_review_branch_name
#    .make_review_branch_name_from_tracker
#
# Public Functions:
#   getReviewBranchPrefix
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
#   WB_DICT_STATUS_DESC
#   BranchPair
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections

import phlgitu_ref
import phlsys_string


WB_STATUS_OK = "ok"
WB_STATUS_PREFIX_BAD = "bad_"
WB_STATUS_BAD_NAME = WB_STATUS_PREFIX_BAD + "name"
WB_STATUS_BAD_PREREVIEW = WB_STATUS_PREFIX_BAD + "prerev"
WB_STATUS_BAD_INREVIEW = WB_STATUS_PREFIX_BAD + "inrev"
WB_STATUS_BAD_LAND = WB_STATUS_PREFIX_BAD + "land"

WB_DICT_STATUS_DESC = {
    WB_STATUS_OK:            "ok",
    WB_STATUS_BAD_NAME:      "branch name is invalid",
    WB_STATUS_BAD_PREREVIEW: "didn't manage to create a review",
    WB_STATUS_BAD_INREVIEW:  "bad update during review",
    WB_STATUS_BAD_LAND:      "didn't manage to land the change",
}


class Error(Exception):
    pass


def getReviewBranchPrefix():
    # don't see a reason to change this atm
    return "arcyd-review/"


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
        self._review_name = self._naming.make_review_branch_name_from_tracker(
            self)
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


class ClassicNaming(object):

    def __init__(self):
        super(ClassicNaming, self).__init__()
        self._tracking_branch_prefix = 'dev/arcyd/'
        self._reserve_branch_prefix = 'dev/arcyd/reserve'
        self._review_branch_prefix = 'arcyd-review/'
        self._remote = 'origin'

    def make_tracker_branch_from_name(self, branch_name):
        """Return the WorkingBranch for 'branch_name' or None if invalid.

        Usage example:
            >>> naming = ClassicNaming()
            >>> make_branch = naming.make_tracker_branch_from_name
            >>> make_branch('dev/arcyd/ok/mywork/master/99')
            ... # doctest: +NORMALIZE_WHITESPACE
            abdt_naming.TrackerBranch("dev/arcyd/ok/mywork/master/99")

            >>> make_branch('invalid/mywork/master')
            Traceback (most recent call last):
                ...
            Error

        :branch_name: string name of the working branch
        :returns: WorkingBranch or None if invalid

        """
        if branch_name == self._reserve_branch_prefix:
            raise Error()  # ignore the reserved branch

        suffix = phlsys_string.after_prefix(
            branch_name, self._tracking_branch_prefix)

        if not suffix:
            raise Error()  # review branches must start with the prefix

        parts = suffix.split("/")
        if len(parts) < 4:
            raise Error()  # suffix should be status/description/base(/...)/id

        base = '/'.join(parts[2:-1])

        return TrackerBranch(
            naming=self,
            branch=branch_name,
            status=parts[0],
            description=parts[1],
            base=base,
            rev_id=parts[-1],
            remote=self._remote)

    def make_tracker_branch_name(self, status, description, base, review_id):
        """Return the unique string name of the tracker branch for params.

        Working branches are of the form:
            <working branch prefix>/description/base

        Usage example:
            >>> naming = ClassicNaming()
            >>> make_name = naming.make_tracker_branch_name
            >>> make_name('ok', 'mywork', 'master',  99)
            'dev/arcyd/ok/mywork/master/99'

        :description: string descriptive name of the branch
        :base: string name of the branch to diff against and land on
        :id: identifier for the review, converted to str() for convenience
        :returns: string name of the working branch

        """
        tracker_branch = ""
        tracker_branch += self._tracking_branch_prefix
        tracker_branch += status
        tracker_branch += "/" + description
        tracker_branch += "/" + base
        tracker_branch += "/" + str(review_id)
        return tracker_branch

    def make_review_branch_from_name(self, branch_name):
        """Return the ReviewBranch for 'branch_name' or None if invalid.

        Usage example:
            >>> naming = ClassicNaming()
            >>> make_branch = naming.make_review_branch_from_name
            >>> make_branch('arcyd-review/mywork/master')
            ... # doctest: +NORMALIZE_WHITESPACE
            abdt_naming.ReviewBranch("arcyd-review/mywork/master")

            >>> make_branch('invalid/mywork/master')
            Traceback (most recent call last):
                ...
            Error

        :branch_name: string name of the review branch
        :returns: ReviewBranch or None if invalid

        """
        suffix = phlsys_string.after_prefix(
            branch_name, self._review_branch_prefix)
        if not suffix:
            raise Error()  # review branches must start with the prefix

        parts = suffix.split("/")
        if len(parts) < 2:
            raise Error()  # suffix should be description/base(/...)

        base = '/'.join(parts[1:])

        return ReviewBranch(
            naming=self,
            branch=branch_name,
            description=parts[0],
            base=base,
            remote=self._remote)

    def make_review_branch_name(self, description, base):
        """Return the unique string name of the review branch for these params.

        Review branches are of the form:
            <review branch prefix>/description/base

        Usage Example:
            >>> naming = ClassicNaming()
            >>> make_name = naming.make_review_branch_name
            >>> make_name('mywork', 'master')
            'arcyd-review/mywork/master'

        :description: string descriptive name of the branch
        :base: string name of the branch to diff against and land on
        :returns: string name of the review branch

        """
        branch_name = self._review_branch_prefix
        branch_name += description
        branch_name += "/" + base
        return branch_name

    def make_review_branch_name_from_tracker(self, tracker_branch):
        """Return the string review branch name for 'working_branch'.

        :working_branch: a WorkingBranch
        :returns: the string review branch name for 'working_branch'

        """
        branch_name = self._review_branch_prefix
        branch_name += tracker_branch.description
        branch_name += "/" + tracker_branch.base
        return branch_name


def _get_branches(branch_list, func):
    """Return a list of branches made by func() from strings in 'branch_list'.

    Strings that aren't valid working branch names are ignored, 'func' is
    expected to raise Error in this case.

    Usage example:
        >>> naming = ClassicNaming()
        >>> func = naming.make_tracker_branch_from_name
        >>> _get_branches(['dev/arcyd/ok/mywork/master/99'], func)
        ... # doctest: +NORMALIZE_WHITESPACE
        [abdt_naming.TrackerBranch("dev/arcyd/ok/mywork/master/99")]

        >>> _get_branches([], func)
        []

        >>> _get_branches(['invalid'], func)
        []

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


def get_branch_pairs(branch_list):
    """Return a list of BranchPair where items in 'branch_list' are suitable.

    Note that if a review_branch or tracker_branch does not have a pair then
    the other member of the tuple is set to 'None'.

    :branch_list: a list of branch name strings to generate the pairs from
    :returns: a list of BranchPair where items in 'branch_list' are suitable

    """
    naming = ClassicNaming()
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
