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
#   makeReviewBranchName
#   makeWorkingBranchName
#   makeReviewBranchFromName
#   getWorkingBranches
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


def makeReviewBranchNameFromWorkingBranch(working_branch):
    """Return the string review branch name for 'working_branch'.

    :working_branch: a WorkingBranch
    :returns: the string review branch name for 'working_branch'

    """
    branch_name = getReviewBranchPrefix()
    branch_name += working_branch.description
    branch_name += "/" + working_branch.base
    return branch_name


def makeReviewBranchName(description, base):
    """Return the unique string name of the review branch for these params.

    Review branches are of the form:
        <review branch prefix>/description/base

    Usage Example:
        >>> makeReviewBranchName('mywork', 'master')
        'arcyd-review/mywork/master'

    :description: string descriptive name of the branch
    :base: string name of the branch to diff against and land on
    :returns: string name of the review branch

    """
    branch_name = getReviewBranchPrefix()
    branch_name += description
    branch_name += "/" + base
    return branch_name


def makeWorkingBranchName(status, description, base, review_id):
    """Return the unique string name of the working branch for these params.

    Working branches are of the form:
        <working branch prefix>/description/base

    Usage example:
        >>> makeWorkingBranchName('ok', 'mywork', 'master',  99)
        'dev/arcyd/ok/mywork/master/99'

    :description: string descriptive name of the branch
    :base: string name of the branch to diff against and land on
    :id: identifier for the review, converted to str() for convenience
    :returns: string name of the working branch

    """
    working_branch = ""
    working_branch += getWorkingBranchPrefix()
    working_branch += status
    working_branch += "/" + description
    working_branch += "/" + base
    working_branch += "/" + str(review_id)
    return working_branch


def makeReviewBranchFromName(branch_name):
    """Return the ReviewBranch for 'branch_name' or None if invalid.

    Usage example:
        >>> makeReviewBranchFromName('arcyd-review/mywork/master')
        ... # doctest: +NORMALIZE_WHITESPACE
        abdt_naming__ReviewBranch(branch='arcyd-review/mywork/master',
                                  description='mywork',
                                  base='master')

        >>> makeReviewBranchFromName('invalid/mywork/master')

    :branch_name: string name of the review branch
    :returns: ReviewBranch or None if invalid

    """
    suffix = phlsys_string.after_prefix(branch_name, getReviewBranchPrefix())
    if not suffix:
        return None  # review branches must start with the prefix

    parts = suffix.split("/")
    if len(parts) < 2:
        return None  # suffix should be description/base(/...)

    return ReviewBranch(
        branch=branch_name,
        description=parts[0],
        base='/'.join(parts[1:]))


class ClassicNaming(object):

    def __init__(self):
        super(ClassicNaming, self).__init__()
        self._tracking_branch_prefix = 'dev/arcyd/'
        self._reserve_branch_prefix = 'dev/arcyd/reserve'

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


def getWorkingBranches(branch_list):
    """Return a list of WorkingBranch made from strings in 'branch_list'.

    Strings that aren't valid working branch names are ignored.

    Usage example:
        >>> getWorkingBranches(['dev/arcyd/ok/mywork/master/99'])
        ... # doctest: +NORMALIZE_WHITESPACE
        [abdt_naming__WorkingBranch(branch='dev/arcyd/ok/mywork/master/99',
                                   status='ok',
                                   description='mywork',
                                   base='master',
                                   id='99')]

        >>> getWorkingBranches([])
        []

        >>> getWorkingBranches(['invalid'])
        []

    :branch_list: list of branch name strings
    :returns: list of WorkingBranch

    """
    working_branch_list = []
    naming = ClassicNaming()
    for branch in branch_list:
        try:
            working_branch_list.append(
                naming.make_tracker_branch_from_name(branch))
        except Error:
            pass  # ignore naming errors, we only want the valid branches
    return working_branch_list


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
