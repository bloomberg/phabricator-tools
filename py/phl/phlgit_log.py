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
from __future__ import division
from __future__ import print_function

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


def get_range_to_here_hashes(repo, start):
    """Return a list of strings corresponding to commits from 'start' to here.

    The list begins with the revision closest to but not including 'start'.
    Raise a ValueError if any of the returned values are not valid hexadecimal.

    :repo: a callable supporting git commands, e.g. repo("status")
    :start: a reference that log will understand
    :returns: a list of strings corresponding to commits from 'start' to here.

    """
    hashes = repo("log", start + "..", "--format=%H").split()
    if not all(c in string.hexdigits for s in hashes for c in s):
        raise ValueError(
            "phlgit_log__getRangeToHereHashes() invalid hashes\n" +
            str(hashes))
    hashes.reverse()
    return hashes


def get_last_n_commit_hashes(repo, n):
    """Return a list of strings corresponding to the last commits.

    The list begins with the oldest revision.
    Raise a ValueError if any of the returned values are not valid hexadecimal.
    Raise an Exception if less values than expected are returned.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: a string corresponding to the last commit ('HEAD')

    """
    return get_last_n_commit_hashes_from_ref(repo, n, 'HEAD')


def get_last_commit_hash(repo):
    """Return a string corresponding to the last commit ('HEAD').

    Raise a ValueError if the returned value is not valid hexadecimal.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: a string corresponding to the last commit ('HEAD')

    """
    return get_last_commit_hash_from_ref(repo, 'HEAD')


def get_last_n_commit_hashes_from_ref(repo, n, ref):
    """Return a list of strings corresponding to the last 'n' commits at 'ref'.

    The list begins with the oldest revision.
    Raise a ValueError if any of the returned values are not valid hexadecimal.
    Raise an Exception if less values than expected are returned.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: a string corresponding to the last commit ('HEAD')

    """
    assert n >= 0
    hashes = repo("log", ref, "-n", str(n), "--format=%H").split()
    if len(hashes) < n:
        raise ValueError(
            "less hashes than expected\n" + str(hashes))
    if not all(c in string.hexdigits for s in hashes for c in s):
        raise ValueError(
            "phlgit_log__getLastNCommitHashesFromRef() invalid hashes\n" +
            str(hashes))
    hashes.reverse()
    return hashes


def get_last_commit_hash_from_ref(repo, ref):
    """Return a string corresponding to the commit referred to by 'ref'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :ref: a reference that log will understand
    :returns: a string corresponding to the commit referred to by 'ref'

    """
    return get_last_n_commit_hashes_from_ref(repo, 1, ref)[0]


def get_range_hashes(repo, start, end):
    """Return a list of strings corresponding to commits from 'start' to 'end'.

    The list begins with the revision closest to but not including 'start'.
    Raise a ValueError if any of the returned values are not valid hexadecimal.

    :repo: a callable supporting git commands, e.g. repo("status")
    :start: a reference that log will understand
    :end: a reference that log will understand
    :returns: a list of strings corresponding to commits from 'start' to 'end'.

    """
    assert repo("rev-parse", "--revs-only", start)
    assert repo("rev-parse", "--revs-only", end)
    hashes = repo("log", start + ".." + end, "--format=%H").split()
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


def make_revision_from_hash(repo, commitHash):
    """Return a 'phlgit_log__Revision' based on 'commitHash' from the repo.
    Raise an exception if the repo does not return a valid FullMessage from the
    commitHash.

    :repo: a callable supporting git commands, e.g. repo("status")
    :commitHash: a string containing the hash to get the message of
    :returns: a 'phlgit_log__Revision' based on the 'commitHash'

    """
    fmt = "%H%n%h%n%ae%n%an%n%ce%n%cn%n%s%n%b"
    fullMessage = repo("log", commitHash + "^!", "--format=" + fmt)
    revision = make_revision_from_full_message(fullMessage)
    return revision


def make_revisions_from_hashes(repo, hashes):
    """Return a list of 'phlgit_log__Revision' from 'hashes'.

    Raise an exception if the repo does not return a valid FullMessage
    from any of 'hashes'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: a list of 'phlgit_log__Revision'

    """
    revisions = [make_revision_from_hash(repo, h) for h in hashes]
    return revisions


def get_author_names_emails_from_hashes(repo, hashes):
    """Return list of (name, email) of the committers in 'hashes'.

    Authors will only appear in the list once, at their earliest appearance.
    The email address is considered as the unique key for each author, so
    someone appearing multiple times with different names but the same email
    will only appear once in the list.

    Raise an exception if the repo does not return a valid FullMessage from
    the commitHash.

    :repo: a callable supporting git commands, e.g. repo("status")
    :hashes: a list of strings containing the hashes to get the messages of
    :returns: a list of unique committer emails in commit order from 'start..'

    """
    revisions = make_revisions_from_hashes(repo, hashes)
    observedEmails = set()
    uniqueAuthors = []
    for r in revisions:
        email = r.author_email
        name = r.author_name
        if email not in observedEmails:
            observedEmails.add(email)
            uniqueAuthors.append((name, email))
    return uniqueAuthors


def get_range_to_here_raw_body(repo, start):
    # TODO: we actually want something that can return an list of bodies
    # TODO: '-n ' '1' is a hack until we return a list
    return repo("log", start + "..", "--format=format:%B", "-n", "1")


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
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
