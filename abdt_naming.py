"""Naming conventions for abd"""

import collections
import doctest
import unittest

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


def getReviewBranchPrefix():
    # don't see a reason to change this atm
    return "ph-review/"


def getWorkingBranchPrefix():
    # this may want to be configurable from the command-line, we'll probably
    # want to wrap the functions in this module in a class and store the
    # convention variables per-instance; will get the whole thing working
    # first and worry about that later.
    return "dev/phab/"


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


def isReviewBranchPrefixed(name):
    prefix = getReviewBranchPrefix()
    return (len(name) > len(prefix)) and name.startswith(prefix)


def getWithoutPrefix(string, prefix):
    """Return 'string' with 'prefix' removed.

    If 'string' does not start with 'prefix' then None is returned.

    Usage examples:

    >>> getWithoutPrefix('dog/cat/', 'dog/')
    'cat/'

    >>> getWithoutPrefix('dog/cat/', 'mouse/')

    :string: string to operate on
    :prefix: string prefix to remove
    :returns: string representing 'string' with 'prefix' removed or None

    """
    if string.startswith(prefix):
        return string[len(prefix):]
    return None


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
        'ph-review/mywork/master'

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
        'dev/phab/ok/mywork/master/99'

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
        >>> makeReviewBranchFromName('ph-review/mywork/master')
        ... # doctest: +NORMALIZE_WHITESPACE
        abdt_naming__ReviewBranch(branch='ph-review/mywork/master',
                                  description='mywork',
                                  base='master')

        >>> makeReviewBranchFromName('invalid/mywork/master')

    :branch_name: string name of the review branch
    :returns: ReviewBranch or None if invalid

    """
    suffix = getWithoutPrefix(branch_name, getReviewBranchPrefix())
    if not suffix:
        return None  # review branches must start with the prefix

    parts = suffix.split("/")
    if len(parts) < 2:
        return None  # suffix should be description/base(/...)

    return ReviewBranch(
        branch=branch_name,
        description=parts[0],
        base='/'.join(parts[1:]))


def makeWorkingBranchFromName(branch_name):
    """Return the WorkingBranch for 'branch_name' or None if invalid.

    Usage example:
        >>> makeWorkingBranchFromName('dev/phab/ok/mywork/master/99')
        ... # doctest: +NORMALIZE_WHITESPACE
        abdt_naming__WorkingBranch(branch='dev/phab/ok/mywork/master/99',
                                   status='ok',
                                   description='mywork',
                                   base='master',
                                   id='99')

        >>> makeWorkingBranchFromName('invalid/mywork/master')

    :branch_name: string name of the working branch
    :returns: WorkingBranch or None if invalid

    """
    suffix = getWithoutPrefix(branch_name, getWorkingBranchPrefix())
    if not suffix:
        return None  # review branches must start with the prefix

    parts = suffix.split("/")
    if len(parts) < 4:
        return None  # suffix should be status/description/base(/...)/id

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
        >>> getWorkingBranches(['dev/phab/ok/mywork/master/99'])
        ... # doctest: +NORMALIZE_WHITESPACE
        [abdt_naming__WorkingBranch(branch='dev/phab/ok/mywork/master/99',
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
    prefix = getWorkingBranchPrefix()
    for branch in branch_list:
        if branch.startswith(prefix):
            working_branch_list.append(
                makeWorkingBranchFromName(branch))
    return working_branch_list


class TestNaming(unittest.TestCase):

    def test(self):
        b = "invalidreviewname"
        self.assertFalse(isReviewBranchPrefixed(b))
        self.assertFalse(makeReviewBranchFromName(b))
        self.assertFalse(makeWorkingBranchFromName(b))

        b = getReviewBranchPrefix()
        self.assertFalse(isReviewBranchPrefixed(b))
        self.assertFalse(makeReviewBranchFromName(b))
        self.assertFalse(makeWorkingBranchFromName(b))

        b = makeReviewBranchName("mywork", "master")
        self.assertTrue(isReviewBranchPrefixed(b))
        r = makeReviewBranchFromName(b)
        self.assertTrue(r)
        self.assertEqual(r.branch, b)
        self.assertEqual(r.description, "mywork")
        self.assertEqual(r.base, "master")
        self.assertFalse(makeWorkingBranchFromName(b))

        b = makeWorkingBranchName("ok", "mywork", "master", 1)
        self.assertFalse(isReviewBranchPrefixed(b))
        self.assertFalse(makeReviewBranchFromName(b))
        w = makeWorkingBranchFromName(b)
        self.assertTrue(w)
        self.assertEqual(w.branch, b)
        self.assertEqual(w.status, "ok")
        self.assertEqual(w.description, "mywork")
        self.assertEqual(w.base, "master")
        self.assertEqual(w.id, "1")


if __name__ == "__main__":
    doctest.testmod()
    unittest.main()

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
