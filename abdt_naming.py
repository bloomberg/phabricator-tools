"""Naming conventions for abd"""

import collections
import doctest
import unittest


def getReviewBranchPrefix():
    # don't see a reason to change this atm
    return "ph-review/"


def getWorkingBranchPrefix():
    return "dev/phab/"


def isReviewBranchName(name):
    prefix = getReviewBranchPrefix()
    return (len(name) > len(prefix)) and name.startswith(prefix)


def getWithoutPrefix(s, prefix):
    """Return 's' with 'prefix removed.

    If 's' does not start with 'prefix' then None is returned.

    Usage examples:

    >>> getWithoutPrefix('dog/cat/', 'dog/')
    'cat/'

    >>> getWithoutPrefix('dog/cat/', 'mouse/')

    :s: string to operate on
    :prefix: string prefix to remove
    :returns: string representing 's' with 'prefix' removed or None

    """
    if s.startswith(prefix):
        return s[len(prefix):]
    return None


WorkingBranch = collections.namedtuple(
    "abdt_naming__WorkingBranch", ["original", "description", "base", "id"])
ReviewBranch = collections.namedtuple(
    "abdt_naming__ReviewBranch", ["original", "description", "base"])


def makeReviewBranchNameFromWorkingBranch(workingBranch):
    """Return the string review branch name for 'workingBranch'.

    :workingBranch: a WorkingBranch
    :returns: the string review branch name for 'workingBranch'

    """
    b = getReviewBranchPrefix()
    b += workingBranch.description
    b += "/" + workingBranch.base
    return b


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
    b = getReviewBranchPrefix()
    b += description
    b += "/" + base
    return b


def makeWorkingBranchName(description, base, review_id):
    """Return the unique string name of the working branch for these params.

    Working branches are of the form:
        <working branch prefix>/description/base

    Usage example:
        >>> makeWorkingBranchName('mywork', 'master',  99)
        'dev/phab/mywork/master/99'

    :description: string descriptive name of the branch
    :base: string name of the branch to diff against and land on
    :id: integer identifier for the review
    :returns: string name of the working branch

    """
    wb = ""
    wb += "dev/phab"
    wb += "/" + description
    wb += "/" + base
    wb += "/" + str(review_id)
    return wb


def makeReviewBranchFromName(branch_name):
    """Return the ReviewBranch for 'branch_name' or None if invalid.

    Usage example:
        >>> makeReviewBranchFromName('ph-review/mywork/master')
        ... # doctest: +NORMALIZE_WHITESPACE
        abdt_naming__ReviewBranch(original='ph-review/mywork/master',
                                  description='mywork',
                                  base='master')

        >>> makeReviewBranchFromName('invalid/mywork/master')

    :branch_name: string name of the review branch
    :returns: ReviewBranch or None if invalid

    """
    rb = getWithoutPrefix(branch_name, getReviewBranchPrefix())
    if not rb:
        return None
    rbs = rb.split("/")
    if len(rbs) < 2:
        return None
    return ReviewBranch(
        original=branch_name,
        description=rbs[0],
        base='/'.join(rbs[1:]))


def makeWorkingBranchFromName(branch_name):
    """Return the WorkingBranch for 'branch_name' or None if invalid.

    Usage example:
        >>> makeWorkingBranchFromName('dev/phab/mywork/master/99')
        ... # doctest: +NORMALIZE_WHITESPACE
        abdt_naming__WorkingBranch(original='dev/phab/mywork/master/99',
                                   description='mywork',
                                   base='master',
                                   id='99')

        >>> makeWorkingBranchFromName('invalid/mywork/master')

    :branch_name: string name of the working branch
    :returns: WorkingBranch or None if invalid

    """
    wb = getWithoutPrefix(branch_name, getWorkingBranchPrefix())
    if not wb:
        return None
    wbs = wb.split("/")
    if len(wbs) < 3:
        return None
    return WorkingBranch(
        original=branch_name,
        description=wbs[0],
        base='/'.join(wbs[1:-1]),
        id=wbs[-1])


def getWorkingBranches(branchList):
    """Return a list of WorkingBranch made from strings in 'branchList'.

    Strings that aren't valid working branch names are ignored.

    Usage example:
        >>> getWorkingBranches(['dev/phab/mywork/master/99'])
        ... # doctest: +NORMALIZE_WHITESPACE
        [abdt_naming__WorkingBranch(original='dev/phab/mywork/master/99',
                                   description='mywork',
                                   base='master',
                                   id='99')]

        >>> getWorkingBranches([])
        []

        >>> getWorkingBranches(['invalid'])
        []

    :branchList: list of branch name strings
    :returns: list of WorkingBranch

    """
    workingBranchList = []
    prefix = getWorkingBranchPrefix()
    for b in branchList:
        if b.startswith(prefix):
            workingBranchList.append(
                makeWorkingBranchFromName(b))
    return workingBranchList


class TestNaming(unittest.TestCase):

    def test(self):
        b = "invalidreviewname"
        self.assertFalse(isReviewBranchName(b))
        self.assertFalse(makeReviewBranchFromName(b))
        self.assertFalse(makeWorkingBranchFromName(b))

        b = getReviewBranchPrefix()
        self.assertFalse(isReviewBranchName(b))
        self.assertFalse(makeReviewBranchFromName(b))
        self.assertFalse(makeWorkingBranchFromName(b))

        b = makeReviewBranchName("mywork", "master")
        self.assertTrue(isReviewBranchName(b))
        r = makeReviewBranchFromName(b)
        self.assertTrue(r)
        self.assertEqual(r.original, b)
        self.assertEqual(r.description, "mywork")
        self.assertEqual(r.base, "master")
        self.assertFalse(makeWorkingBranchFromName(b))

        b = makeWorkingBranchName("mywork", "master", 1)
        self.assertFalse(isReviewBranchName(b))
        self.assertFalse(makeReviewBranchFromName(b))
        w = makeWorkingBranchFromName(b)
        self.assertTrue(w)
        self.assertEqual(w.original, b)
        self.assertEqual(w.description, "mywork")
        self.assertEqual(w.base, "master")
        self.assertEqual(w.id, "1")


if __name__ == "__main__":
    doctest.testmod()
    unittest.main()
