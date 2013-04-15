"""Operations combining conduit with git."""

import phlcon_differential
import phlcon_user
import phlgit_log
import phlgitu_ref

import abdt_commitmessage
import abdt_messagefields
import abdt_exception


def getPrimaryNameEmailAndUserFromBranch(clone, conduit, base, branch):
    hashes = phlgit_log.getRangeHashes(clone, base, branch)
    if not hashes:
        raise abdt_exception.AbdUserException("no history to diff")
    commit = hashes[0]
    committer = phlgit_log.getAuthorNamesEmailsFromHashes(clone, [commit])[0]
    name = committer[0]
    email = committer[1]
    user = phlcon_user.queryUsersFromEmails(conduit, [email])[0]
    if not user:
        raise abdt_exception.AbdUserException(
            "first committer is not a Phabricator user")
    return name, email, user


def getAnyUserFromBranch(clone, conduit, base, branch):
    if phlgitu_ref.parseRefHash(clone, base) is None:
        hashes = phlgit_log.getLastNCommitHashesFromRef(clone, 1, branch)
    else:
        hashes = phlgit_log.getRangeHashes(clone, base, branch)

    if not hashes:
        hashes = phlgit_log.getLastNCommitHashesFromRef(clone, 1, branch)
    committers = phlgit_log.getAuthorNamesEmailsFromHashes(clone, hashes)
    emails = [committer[1] for committer in committers]
    users = phlcon_user.queryUsersFromEmails(conduit, emails)
    for user in users:
        if user:
            return user
    raise abdt_exception.AbdUserException(
        "no users on branch!")


def getFieldsFromCommitHashes(conduit, clone, hashes):
    """Return a ParseCommitMessageResponse based on the commit messages.

    :conduit: supports call()
    :clone: supports call()
    :hashes: list of the commit hashes to examine
    :returns: a phlcon_differential.ParseCommitMessageResponse

    """
    d = phlcon_differential
    revisions = phlgit_log.makeRevisionsFromHashes(clone, hashes)
    fields = None
    for r in revisions:
        p = d.parseCommitMessage(
            conduit, r.subject + "\n\n" + r.message)
        f = phlcon_differential.ParseCommitMessageFields(**p.fields)
        fields = abdt_messagefields.update(fields, f)
    message = makeMessageFromFields(conduit, fields)
    return d.parseCommitMessage(conduit, message)


def makeMessageFromFields(conduit, fields):
    """Return a string message generated from the supplied 'fields'.

    :fields: a phlcon_differential.ParseCommitMessageFields
    :returns: a string message

    """
    user_names = None
    if fields.reviewerPHIDs:
        user_names = phlcon_user.queryUsernamesFromPhids(
            conduit, fields.reviewerPHIDs)
    return abdt_commitmessage.make(
        fields.title, fields.summary, fields.testPlan, user_names)


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
