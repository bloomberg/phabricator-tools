"""Naming conventions for abd"""

import collections
import doctest
import unittest


def getReviewBranchPrefix():
    # don't see a reason to change this atm
    return "ph-review/"


def getWorkingBranchPrefix():
    # this may want to be configurable from the command-line, we'll probably
    # want to wrap the functions in this module in a class and store the
    # convention variables per-instance; will get the whole thing working
    # first and worry about that later.
    return "dev/phab/"


def isReviewBranchName(name):
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
        "full_name",
        "description",
        "base",
        "id"])

ReviewBranch = collections.namedtuple(
    "abdt_naming__ReviewBranch", [
        "full_name",
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


def makeWorkingBranchName(description, base, review_id):
    """Return the unique string name of the working branch for these params.

    Working branches are of the form:
        <working branch prefix>/description/base

    Usage example:
        >>> makeWorkingBranchName('mywork', 'master',  99)
        'dev/phab/mywork/master/99'

    :description: string descriptive name of the branch
    :base: string name of the branch to diff against and land on
    :id: identifier for the review, converted to str() for convenience
    :returns: string name of the working branch

    """
    working_branch = ""
    working_branch += "dev/phab"
    working_branch += "/" + description
    working_branch += "/" + base
    working_branch += "/" + str(review_id)
    return working_branch


def makeReviewBranchFromName(branch_name):
    """Return the ReviewBranch for 'branch_name' or None if invalid.

    Usage example:
        >>> makeReviewBranchFromName('ph-review/mywork/master')
        ... # doctest: +NORMALIZE_WHITESPACE
        abdt_naming__ReviewBranch(full_name='ph-review/mywork/master',
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
        full_name=branch_name,
        description=parts[0],
        base='/'.join(parts[1:]))


def makeWorkingBranchFromName(branch_name):
    """Return the WorkingBranch for 'branch_name' or None if invalid.

    Usage example:
        >>> makeWorkingBranchFromName('dev/phab/mywork/master/99')
        ... # doctest: +NORMALIZE_WHITESPACE
        abdt_naming__WorkingBranch(full_name='dev/phab/mywork/master/99',
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
    if len(parts) < 3:
        return None  # suffix should be description/base(/...)/id

    return WorkingBranch(
        full_name=branch_name,
        description=parts[0],
        base='/'.join(parts[1:-1]),
        id=parts[-1])


def getWorkingBranches(branch_list):
    """Return a list of WorkingBranch made from strings in 'branch_list'.

    Strings that aren't valid working branch names are ignored.

    Usage example:
        >>> getWorkingBranches(['dev/phab/mywork/master/99'])
        ... # doctest: +NORMALIZE_WHITESPACE
        [abdt_naming__WorkingBranch(full_name='dev/phab/mywork/master/99',
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
        self.assertEqual(r.full_name, b)
        self.assertEqual(r.description, "mywork")
        self.assertEqual(r.base, "master")
        self.assertFalse(makeWorkingBranchFromName(b))

        b = makeWorkingBranchName("mywork", "master", 1)
        self.assertFalse(isReviewBranchName(b))
        self.assertFalse(makeReviewBranchFromName(b))
        w = makeWorkingBranchFromName(b)
        self.assertTrue(w)
        self.assertEqual(w.full_name, b)
        self.assertEqual(w.description, "mywork")
        self.assertEqual(w.base, "master")
        self.assertEqual(w.id, "1")


if __name__ == "__main__":
    doctest.testmod()
    unittest.main()
