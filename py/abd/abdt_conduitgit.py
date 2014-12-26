"""Operations combining conduit with git."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_conduitgit
#
# Public Functions:
#   getPrimaryUserDetailsFromBranch
#   getAnyUserFromBranch
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abdt_exception


def getPrimaryUserDetailsFromBranch(conduit, branch):
    """Return a tuple representing the primary user on the supplied 'branch'.

    The primary user is currently determined from the latest user to commit
    on the branch but this may change later.

    :conduit: an abdt_conduit
    :branch: an abdt_branch
    :returns: a (name, email, username, phid) tuple

    """
    names_emails = branch.get_author_names_emails()
    if not names_emails:
        raise abdt_exception.NoHistoryException(
            branch.review_branch_name(),
            branch.base_branch_name())
    committer = names_emails[-1]
    name = committer[0]
    email = committer[1]
    found_user = conduit.query_name_and_phid_from_email(email)
    if found_user is None:
        raise abdt_exception.AbdUserException(
            "first committer is not a Phabricator user")
    user, phid = found_user
    return name, email, user, phid


def getAnyUserFromBranch(conduit, branch):
    emails = branch.get_any_author_emails()
    users = conduit.query_users_from_emails(emails)
    for user in users:
        if user:
            return user
    raise abdt_exception.NoUsersOnBranchException(
        branch.review_branch_name(), branch.base_branch_name(), emails)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
