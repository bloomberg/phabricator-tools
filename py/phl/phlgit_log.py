"""Wrapper around 'git log'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_log
#
# Public Functions:
#   get_range_to_here_hashes
#   get_last_n_commit_hashes
#   get_last_commit_hash
#   get_last_n_commit_hashes_from_ref
#   get_last_commit_hash_from_ref
#   get_range_hashes
#   make_revision_from_full_message
#   make_revision_from_hash
#   make_revisions_from_hashes
#   get_author_names_emails_from_hashes
#   get_range_to_here_raw_body
#
# Public Assignments:
#   Revision
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections
import string

"""NamedTuple to represent a git revision.

:hash:the sha1 associated with this revision
:author_email:the email address of the original author
:author_name:the name of the original author
:committer_email:the email address of the committer
:committer_name:the name of the committer
:subject:the first line of the commit message
:message:any subsequent lines of the commit message, empty string if none

"""
Revision = collections.namedtuple(
    "phlgit_log__Revision", [
        'hash',
        'abbrev_hash',
        'author_email', 'author_name',
        'committer_email', 'committer_name',
        'subject',
        'message'
    ])


def get_range_to_here_hashes(clone, start):
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


def get_last_n_commit_hashes(clone, n):
    """Return a list of strings corresponding to the last commits.

    The list begins with the oldest revision.
    Raise a ValueError if any of the returned values are not valid hexadecimal.
    Raise an Exception if less values than expected are returned.

    :clone: supports 'call("log")' with git log parameters
    :returns: a string corresponding to the last commit ('HEAD')

    """
    return get_last_n_commit_hashes_from_ref(clone, n, 'HEAD')


def get_last_commit_hash(clone):
    """Return a string corresponding to the last commit ('HEAD').

    Raise a ValueError if the returned value is not valid hexadecimal.

    :clone: supports 'call("log")' with git log parameters
    :returns: a string corresponding to the last commit ('HEAD')

    """
    return get_last_commit_hash_from_ref(clone, 'HEAD')


def get_last_n_commit_hashes_from_ref(clone, n, ref):
    """Return a list of strings corresponding to the last 'n' commits at 'ref'.

    The list begins with the oldest revision.
    Raise a ValueError if any of the returned values are not valid hexadecimal.
    Raise an Exception if less values than expected are returned.

    :clone: supports 'call("log")' with git log parameters
    :returns: a string corresponding to the last commit ('HEAD')

    """
    assert n >= 0
    hashes = clone.call("log", ref, "-n", str(n), "--format=%H").split()
    if len(hashes) < n:
        raise ValueError(
            "less hashes than expected\n" + str(hashes))
    if not all(c in string.hexdigits for s in hashes for c in s):
        raise ValueError(
            "phlgit_log__getLastNCommitHashesFromRef() invalid hashes\n"
            + str(hashes))
    hashes.reverse()
    return hashes


def get_last_commit_hash_from_ref(clone, ref):
    """Return a string corresponding to the commit referred to by 'ref'.

    :clone: supports 'call("log")' with git log parameters
    :ref: a reference that log will understand
    :returns: a string corresponding to the commit referred to by 'ref'

    """
    return get_last_n_commit_hashes_from_ref(clone, 1, ref)[0]


def get_range_hashes(clone, start, end):
    """Return a list of strings corresponding to commits from 'start' to 'end'.

    The list begins with the revision closest to but not including 'start'.
    Raise a ValueError if any of the returned values are not valid hexadecimal.

    :clone: supports 'call("log")' with git log parameters
    :start: a reference that log will understand
    :end: a reference that log will understand
    :returns: a list of strings corresponding to commits from 'start' to 'end'.

    """
    assert clone.call("rev-parse", "--revs-only", start)
    assert clone.call("rev-parse", "--revs-only", end)
    hashes = clone.call("log", start + ".." + end, "--format=%H").split()
    if not all(c in string.hexdigits for s in hashes for c in s):
        raise ValueError(
            "phlgit_log__getRangeHashes() invalid hashes\n" + str(hashes))
    hashes.reverse()
    return hashes


def make_revision_from_full_message(message):
    """Return a 'phlgit_log__Revision' based on the provided 'message'.

    Raise an Exception if the message doesn't parse successfully.

    :message: 'git log HEAD^! --format:"%H%n%h%n%ae%n%an%n%ce%n%cn%n%s%n%b"'
    :returns: a 'phlgit_log__Revision'

    """
    lines = message.splitlines()
    return Revision(
        hash=lines[0],
        abbrev_hash=lines[1],
        author_email=lines[2],
        author_name=lines[3],
        committer_email=lines[4],
        committer_name=lines[5],
        subject=lines[6],
        message='\n'.join(lines[7:]))


def make_revision_from_hash(clone, commitHash):
    """Return a 'phlgit_log__Revision' based on 'commitHash' from the clone.
    Raise an exception if the clone does not return a valid FullMessage from
    the commitHash.

    :clone: something that supports "call()" with git commands
    :commitHash: a string containing the hash to get the message of
    :returns: a 'phlgit_log__Revision' based on the 'commitHash'

    """
    fmt = "%H%n%h%n%ae%n%an%n%ce%n%cn%n%s%n%b"
    fullMessage = clone.call("log", commitHash + "^!", "--format=" + fmt)
    revision = make_revision_from_full_message(fullMessage)
    return revision


def make_revisions_from_hashes(clone, hashes):
    """Return a list of 'phlgit_log__Revision' from 'hashes'.

    Raise an exception if the clone does not return a valid FullMessage
    from any of 'hashes'.

    :clone: something that supports "call()" with git commands
    :returns: a list of 'phlgit_log__Revision'

    """
    revisions = [make_revision_from_hash(clone, h) for h in hashes]
    return revisions


def get_author_names_emails_from_hashes(clone, hashes):
    """Return list of (name, email) of the committers in 'hashes'.

    Authors will only appear in the list once, at their earliest appearance.
    The email address is considered as the unique key for each author, so
    someone appearing multiple times with different names but the same email
    will only appear once in the list.

    Raise an exception if the clone does not return a valid FullMessage from
    the commitHash.

    :clone: something that supports "call()" with git commands
    :hashes: a list of strings containing the hashes to get the messages of
    :returns: a list of unique committer emails in commit order from 'start..'

    """
    revisions = make_revisions_from_hashes(clone, hashes)
    observedEmails = set()
    uniqueAuthors = []
    for r in revisions:
        email = r.author_email
        name = r.author_name
        if email not in observedEmails:
            observedEmails.add(email)
            uniqueAuthors.append((name, email))
    return uniqueAuthors


def get_range_to_here_raw_body(clone, start):
    # TODO: we actually want something that can return an list of bodies
    # TODO: '-n ' '1' is a hack until we return a list
    return clone.call("log", start + "..", "--format=format:%B", "-n", "1")


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
