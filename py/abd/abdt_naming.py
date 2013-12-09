"""Naming conventions for abd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_naming
#
# Public Classes:
#   Error
#   ClassicNaming
#    .make_tracker_branch_from_name
#    .make_tracker_branch_name
#    .make_review_branch_from_name
#    .make_review_branch_name
#
# Public Functions:
#   getReviewBranchPrefix
#   getWorkingBranchPrefix
#   getReservedBranchPrefix
#   isStatusBad
#   isStatusBadPreReview
#   isStatusBadLand
#   isReviewBranchPrefixed
#   makeReviewBranchNameFromWorkingBranch
#   get_branches
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
#   WorkingBranch
#   ReviewBranch
#   BranchPair
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections

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


def getWorkingBranchPrefix():
    # this may want to be configurable from the command-line, we'll probably
    # want to wrap the functions in this module in a class and store the
    # convention variables per-instance; will get the whole thing working
    # first and worry about that later.
    return "dev/arcyd/"


def getReservedBranchPrefix():
    # this may want to be configurable from the command-line, we'll probably
    # want to wrap the functions in this module in a class and store the
    # convention variables per-instance; will get the whole thing working
    # first and worry about that later.
    return "dev/arcyd/reserve"


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


def isReviewBranchPrefixed(name):
    prefix = getReviewBranchPrefix()
    return (len(name) > len(prefix)) and name.startswith(prefix)


WorkingBranch = collections.namedtuple(
    "abdt_naming__WorkingBranch", [
        "branch",
        "status",
        "description",
        "base",
        "id"])

ReviewBranch = collections.namedtuple(
    "abdt_naming__ReviewBranch", [
        "branch",
        "description",
        "base"])


BranchPair = collections.namedtuple(
    "abdt_naming__BranchPair", [
        "review",
        "tracker"])


def makeReviewBranchNameFromWorkingBranch(working_branch):
    """Return the string review branch name for 'working_branch'.

    :working_branch: a WorkingBranch
    :returns: the string review branch name for 'working_branch'

    """
    branch_name = getReviewBranchPrefix()
    branch_name += working_branch.description
    branch_name += "/" + working_branch.base
    return branch_name


class ClassicNaming(object):

    def __init__(self):
        super(ClassicNaming, self).__init__()
        self._tracking_branch_prefix = 'dev/arcyd/'
        self._reserve_branch_prefix = 'dev/arcyd/reserve'
        self._review_branch_prefix = 'arcyd-review/'

    def make_tracker_branch_from_name(self, branch_name):
        """Return the WorkingBranch for 'branch_name' or None if invalid.

        Usage example:
            >>> naming = ClassicNaming()
            >>> make_branch = naming.make_tracker_branch_from_name
            >>> make_branch('dev/arcyd/ok/mywork/master/99')
            ... # doctest: +NORMALIZE_WHITESPACE
            abdt_naming__WorkingBranch(branch='dev/arcyd/ok/mywork/master/99',
                                    status='ok',
                                    description='mywork',
                                    base='master',
                                    id='99')

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

        return WorkingBranch(
            branch=branch_name,
            status=parts[0],
            description=parts[1],
            base='/'.join(parts[2:-1]),
            id=parts[-1])

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
            abdt_naming__ReviewBranch(branch='arcyd-review/mywork/master',
                                    description='mywork',
                                    base='master')

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

        return ReviewBranch(
            branch=branch_name,
            description=parts[0],
            base='/'.join(parts[1:]))

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


def get_branches(branch_list, func):
    """Return a list of branches made by func() from strings in 'branch_list'.

    Strings that aren't valid working branch names are ignored, 'func' is
    expected to raise Error in this case.

    Usage example:
        >>> naming = ClassicNaming()
        >>> func = naming.make_tracker_branch_from_name
        >>> get_branches(['dev/arcyd/ok/mywork/master/99'], func)
        ... # doctest: +NORMALIZE_WHITESPACE
        [abdt_naming__WorkingBranch(branch='dev/arcyd/ok/mywork/master/99',
                                   status='ok',
                                   description='mywork',
                                   base='master',
                                   id='99')]

        >>> get_branches([], func)
        []

        >>> get_branches(['invalid'], func)
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
    tracker_branches = get_branches(
        branch_list, naming.make_tracker_branch_from_name)
    review_branches = get_branches(
        branch_list, naming.make_review_branch_from_name)

    # XXX: pychecker and pyflakes don't understand dictcomps yet so do it like
    #      this instead
    review_name = makeReviewBranchNameFromWorkingBranch
    name_to_tracked = dict([(review_name(b), b) for b in tracker_branches])
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
