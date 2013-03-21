"""Wrapper around 'git log'"""

import collections
import os
import string
import unittest

import phlsys_git
import phlsys_subprocess

"""NamedTuple to represent a git revision.

:hash:the sha1 associated with this revision
:author:the email address of the original author
:committer:the email address of the committer
:subject:the first line of the commit message
:message:any subsequent lines of the commit message, empty string if none

"""
Revision = collections.namedtuple(
    "phlgit_log__Revision",
    ['hash', 'author', 'committer', 'subject', 'message'])

    # What it does
    # What it returns
    # Essential behaviour
    # Undefined behaviour
    # Note that ...


def getRangeToHereHashes(clone, start):
    """Return a list of strings corresponding to commits from 'start' to here.

    The list begins with the revision closest to but not including 'start'.
    Raise a ValueError if any of the returned values are not valid hexadecimal.

    :clone: supports 'call("log")' with git log parameters
    :start: a reference that log will understand
    :returns: a list of strings corresponding to commits from 'start' to here.

    """
    hashes = clone.call("log", start + "..", "--format=%H").split()
    if not all(c in string.hexdigits for s in hashes for c in s):
        raise ValueError(
            "phlgit_log__getRangeToHereHashes() invalid hashes\n"
            + str(hashes))
    hashes.reverse()
    return hashes


def getLastNCommitHashes(clone, n):
    """Return a list of strings corresponding to the last commits.

    The list begins with the oldest revision.
    Raise a ValueError if any of the returned values are not valid hexadecimal.
    Raise an Exception if less values than expected are returned.

    :clone: supports 'call("log")' with git log parameters
    :returns: a string corresponding to the last commit ('HEAD')

    """
    assert n >= 0
    hashes = clone.call("log", "HEAD", "-n", str(n), "--format=%H").split()
    if len(hashes) < n:
        raise ValueError(
            "less hashes than expected\n" + str(hashes))
    if not all(c in string.hexdigits for s in hashes for c in s):
        raise ValueError(
            "phlgit_log__getLastNCommitHashes() invalid hashes\n"
            + str(hashes))
    hashes.reverse()
    return hashes


def getLastCommitHash(clone):
    """Return a string corresponding to the last commit ('HEAD').

    Raise a ValueError if the returned value is not valid hexadecimal.

    :clone: supports 'call("log")' with git log parameters
    :returns: a string corresponding to the last commit ('HEAD')

    """
    return getLastNCommitHashes(clone, 1)[0]


def getRangeHashes(clone, start, end):
    """Return a list of strings corresponding to commits from 'start' to 'end'.

    The list begins with the revision closest to but not including 'start'.
    Raise a ValueError if any of the returned values are not valid hexadecimal.

    :clone: supports 'call("log")' with git log parameters
    :start: a reference that log will understand
    :end: a reference that log will understand
    :returns: a list of strings corresponding to commits from 'start' to 'end'.

    """
    hashes = clone.call("log", start + ".." + end, "--format=%H").split()
    if not all(c in string.hexdigits for s in hashes for c in s):
        raise ValueError(
            "phlgit_log__getRangeHashes() invalid hashes\n" + str(hashes))
    hashes.reverse()
    return hashes


def makeRevisionFromFullMessage(message):
    """Return a 'phlgit_log__Revision' based on the provided 'message'.

    Raise an Exception if the message doesn't parse successfully.

    :message: message from 'git log HEAD^! --format:"%H%n%ae%n%ce%n%s%n%b"'
    :returns: a 'phlgit_log__Revision'

    """
    lines = message.splitlines()
    return Revision(
        hash=lines[0],
        author=lines[1],
        committer=lines[2],
        subject=lines[3],
        message='\n'.join(lines[4:]))


def makeRevisionFromHash(clone, commitHash):
    """Return a 'phlgit_log__Revision' based on 'commitHash' from the clone.
    Raise an exception if the clone does not return a valid FullMessage from
    the commitHash

    :clone: something that supports "call()" with git commands
    :commitHash: a string containing the hash to get the message of
    :returns: a 'phlgit_log__Revision' based on the 'commitHash'

    """
    fmt = "%H%n%ae%n%ce%n%s%n%b"
    fullMessage = clone.call("log", commitHash + "^!", "--format=" + fmt)
    revision = makeRevisionFromFullMessage(fullMessage)
    return revision


def makeRevisionsFromHashes(clone, hashes):
    """Return a list of 'phlgit_log__Revision' from 'hashes'.
    Raise an exception if the clone does not return a valid FullMessage from
    any of 'hashes'.

    :clone: something that supports "call()" with git commands
    :returns: a list of 'phlgit_log__Revision'

    """
    return [makeRevisionFromHash(clone, h) for h in hashes]


def getCommittersFromHashes(clone, hashes):
    """Return string list of the email addresses of the committers in 'hashes'.

    Committers will only appear in the list once, at their earliest appearance.
    Raise an exception if the clone does not return a valid FullMessage from
    the commitHash.

    :clone: something that supports "call()" with git commands
    :hashes: a list of strings containing the hashes to get the messages of
    :returns: a list of unique committer emails in commit order from 'start..'

    """
    revisions = makeRevisionsFromHashes(clone, hashes)
    observedAuthors = set()
    uniqueAuthors = []
    for r in revisions:
        author = r.author
        if author not in observedAuthors:
            observedAuthors.add(author)
            uniqueAuthors.append(author)
    return uniqueAuthors


def getRangeToHereRawBody(clone, start):
    # TODO: we actually want something that can return an list of bodies
    # TODO: '-n ' '1' is a hack until we return a list
    return clone.call("log", start + "..", "--format=format:%B", "-n", "1")


class TestLog(unittest.TestCase):

    def setUp(self):
        # TODO: make this more portable with shutil etc.
        self.run = phlsys_subprocess.run
        self.runCommands = phlsys_subprocess.runCommands
        self.path = "phlgit_diff_TestDiff"
        self.runCommands("mkdir " + self.path)
        self.run("git", "init", workingDir=self.path)
        self.clone = phlsys_git.GitClone(self.path)
        self.authorName = "No one"
        self.authorEmail = "noone@nowhere.com"
        self.author = self.authorName + " <" + self.authorEmail + ">"

    def _createCommitNewFile(self, filename, subject=None, message=None):
        self.runCommands("touch " + os.path.join(self.path, filename))
        self.clone.call("add", filename)
        if not subject:
            if message:
                raise Exception("didn't expect message with empty subject")
            self.clone.call(
                "commit", "-a", "-m", filename,
                "--author", self.author)
        elif not message:
            self.clone.call(
                "commit", "-a", "-m", subject,
                "--author", self.author)
        else:
            message = subject + "\n\n" + message
            self.clone.call(
                "commit", "-a", "-m", message,
                "--author", self.author)

#     def testNoCommits(self):
#         hashes = getRangeToHereHashes(self.clone, "HEAD")
#         self.assertIsNotNone(hashes)
#         self.assertTrue(not hashes)
#         self.assertIsInstance(hashes, list)
#         head = getLastCommitHash(self.clone)
#         self.assertIsNone(head)
#         head2 = getLastNCommitHashes(self.clone, 1)
#         self.assertIsNotNone(head2)
#         self.assertEqual(head, head2[0])

    def testOneCommit(self):
        self._createCommitNewFile("README")
        hashes = getRangeToHereHashes(self.clone, "HEAD")
        self.assertIsNotNone(hashes)
        self.assertTrue(not hashes)
        self.assertIsInstance(hashes, list)
        head = getLastCommitHash(self.clone)
        self.assertIsNotNone(head)
        head2 = getLastNCommitHashes(self.clone, 1)
        self.assertIsNotNone(head2)
        self.assertEqual(head, head2[0])
        self.assertListEqual(getLastNCommitHashes(self.clone, 0), [])
        self.assertRaises(ValueError, getLastNCommitHashes, self.clone, 2)

    def testTwoCommits(self):
        self._createCommitNewFile("README")
        self._createCommitNewFile("README2")
        head = getLastCommitHash(self.clone)
        self.assertIsNotNone(head)
        hashes = getLastNCommitHashes(self.clone, 2)
        self.assertIsNotNone(hashes)
        self.assertEqual(head, hashes[-1])
        self.assertListEqual(hashes, hashes)

    def testSimpleFork(self):
        self._createCommitNewFile("README")
        self.clone.call("branch", "fork")
        self._createCommitNewFile("ONLY_MASTER")
        self.clone.call("checkout", "fork")
        self._createCommitNewFile("ONLY_FORK", "ONLY_FORK", "BODY\nBODY")
        self._createCommitNewFile("ONLY_FORK2")

        log = getRangeToHereRawBody(self.clone, "master")
        self.assertIn("ONLY_FORK", log)
        self.assertNotIn("ONLY_MASTER", log)
        self.assertNotIn("README", log)

        hashes = getRangeToHereHashes(self.clone, "master")
        hashes2 = getRangeHashes(self.clone, "master", "fork")
        self.assertListEqual(hashes, hashes2)
        r0 = makeRevisionFromHash(self.clone, hashes[0])
        self.assertEqual(r0.subject, "ONLY_FORK")
        self.assertEqual(r0.message.strip(), "BODY\nBODY")
        r1 = makeRevisionFromHash(self.clone, hashes[1])
        self.assertEqual(r1.subject, "ONLY_FORK2")
        self.assertIsNotNone(r1.message)
        self.assertIsInstance(r1.message, str)

        committers = getCommittersFromHashes(self.clone, hashes)
        self.assertEqual(len(committers), 1)
        self.assertEqual(committers[0], self.authorEmail)

    def tearDown(self):
        self.runCommands("rm -rf " + self.path)


if __name__ == "__main__":
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
