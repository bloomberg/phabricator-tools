"""Operations combining conduit with git."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_conduitgit
#
# Public Functions:
#   getPrimaryNameEmailAndUserFromBranch
#   getAnyUserFromBranch
#   getFieldsFromCommitHash
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import phlgit_log
import phlgitu_ref

import abdt_exception


def getPrimaryNameEmailAndUserFromBranch(clone, conduit, base, branch):
    hashes = phlgit_log.get_range_hashes(clone, base, branch)
    if not hashes:
        raise abdt_exception.AbdUserException("no history to diff")
    commit = hashes[-1]
    committer = phlgit_log.get_author_names_emails_from_hashes(
        clone, [commit])[0]
    name = committer[0]
    email = committer[1]
    user = conduit.query_users_from_emails([email])[0]
    if not user:
        raise abdt_exception.AbdUserException(
            "first committer is not a Phabricator user")
    return name, email, user


def getAnyUserFromBranch(clone, conduit, base, branch):
    if phlgitu_ref.parse_ref_hash(clone, base) is None:
        hashes = phlgit_log.get_last_n_commit_hashes_from_ref(clone, 1, branch)
    else:
        hashes = phlgit_log.get_range_hashes(clone, base, branch)

    if not hashes:
        hashes = phlgit_log.get_last_n_commit_hashes_from_ref(clone, 1, branch)
    committers = phlgit_log.get_author_names_emails_from_hashes(clone, hashes)
    emails = [committer[1] for committer in committers]
    users = conduit.query_users_from_emails(emails)
    for user in users:
        if user:
            return user
    raise abdt_exception.NoUsersOnBranchException(branch, base, emails)


def getFieldsFromCommitHash(conduit, clone, commit_hash, defaultTestPlan=None):
    """Return a ParseCommitMessageResponse based on the commit message.

    :conduit: supports call()
    :clone: supports call()
    :commit_hash: a single commit hash to get the message from
    :returns: a phlcon_differential.ParseCommitMessageResponse

    """
    revision = phlgit_log.make_revision_from_hash(clone, commit_hash)
    message = revision.subject + "\n"
    message += "\n"
    message += revision.message + "\n"
    parsed = conduit.parse_commit_message(message)

    testPlan = "testPlan"
    if defaultTestPlan is not None:
        if parsed.fields is not None:
            if not testPlan in parsed.fields or not parsed.fields[testPlan]:
                message += "Test Plan:\n" + defaultTestPlan
                parsed = conduit.parse_commit_message(message)

    return parsed


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
