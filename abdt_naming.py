"""Naming conventions for abd"""

import collections
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
    if s.startswith(prefix):
        return s[len(prefix):]
    return None


WorkingBranch = collections.namedtuple(
    "abdt_naming__WorkingBranch", ["original", "description", "base", "id"])
ReviewBranch = collections.namedtuple(
    "abdt_naming__ReviewBranch", ["original", "description", "base"])


def makeReviewBranchNameFromWorkingBranch(wb):
    b = getReviewBranchPrefix()
    b += wb.description
    b += "/" + wb.base
    return b


def makeReviewBranchName(description, base):
    b = getReviewBranchPrefix()
    b += description
    b += "/" + base
    return b


def makeWorkingBranchName(description, base, id):
    wb = ""
    wb += "dev/phab"
    wb += "/" + description
    wb += "/" + base
    wb += "/" + str(id)
    return wb


def makeReviewBranchFromName(b):
    rb = getWithoutPrefix(b, getReviewBranchPrefix())
    if not rb:
        return None
    rbs = rb.split("/")
    if len(rbs) < 2:
        return None
    return ReviewBranch(
        original=b,
        description=rbs[0],
        base='/'.join(rbs[1:]))


def makeWorkingBranchFromName(b):
    wb = getWithoutPrefix(b, getWorkingBranchPrefix())
    if not wb:
        return None
    wbs = wb.split("/")
    if len(wbs) < 3:
        return None
    return WorkingBranch(
        original=b,
        description=wbs[0],
        base='/'.join(wbs[1:-1]),
        id=wbs[-1])


def getWorkingBranches(branchList):
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
    unittest.main()
