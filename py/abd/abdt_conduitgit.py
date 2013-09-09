"""Operations combining conduit with git."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_conduitgit
#
# Public Functions:
#   getPrimaryNameEmailAndUserFromBranch
#   getAnyUserFromBranch
#   getFieldsFromBranch
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import abdt_exception


def getPrimaryNameEmailAndUserFromBranch(conduit, branch):
    names_emails = branch.get_author_names_emails()
    if not names_emails:
        raise abdt_exception.AbdUserException("no history to diff")
    committer = names_emails[-1]
    name = committer[0]
    email = committer[1]
    user = conduit.query_users_from_emails([email])[0]
    if not user:
        raise abdt_exception.AbdUserException(
            "first committer is not a Phabricator user")
    return name, email, user


def getAnyUserFromBranch(conduit, branch):
    emails = branch.get_any_author_emails()
    users = conduit.query_users_from_emails(emails)
    for user in users:
        if user:
            return user
    raise abdt_exception.NoUsersOnBranchException(
        branch.review_branch_name(), branch.base_branch_name(), emails)


def getFieldsFromBranch(conduit, branch, defaultTestPlan=None):
    """Return a ParseCommitMessageResponse based on the branch.

    :conduit: supports call()
    :branch: the branch to get fields from
    :defaultTestPlan: the test plan to go with if none discovered on branch
    :returns: a phlcon_differential.ParseCommitMessageResponse

    """
    message = branch.get_commit_message_from_tip()
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
