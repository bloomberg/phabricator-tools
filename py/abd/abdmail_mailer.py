"""Send mails to interested parties about pre-specified conditions."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdmail_mailer
#
# Public Classes:
#   Mailer
#    .noUsersOnBranch
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import textwrap
import types


class Mailer(object):

    """Send mails to interested parties about pre-specified conditions."""

    def __init__(self, mail_sender, admin_emails, repository_name, uri):
        """Initialise, simply store the supplied parameters.

        :mail_sender: supports send(to, cc, subject, message)
        :admin_emails: list of string, who to tell when no appropriate users
        :repository_name: the repository that is in context
        :uri: the address of the phabricator instance

        """
        self._mail_sender = mail_sender
        assert not isinstance(
            admin_emails, types.StringTypes), "should be list not string"
        self._admin_emails = admin_emails
        self._repository_name = repository_name
        self._uri = uri

    def noUsersOnBranch(self, branch_name, branch_base, emails):
        # TODO: determine which of 'emails' we're permitted to send to
        msg = textwrap.dedent("""\
            No registered Phabricator users were found when
            trying to create a review from a branch.

            repository:     {repo}
            branch:         {branch}
            base branch:    {base_branch}
            unknown emails: {emails}

            If you appear in the 'unknown emails' list then
            please register by visiting this link, simply
            logging in and registering your email address will
            resolve the issue:

                {uri}

            You are receiving this message because you are
            either in the unknown email list or an admin.

            If you want to / have to use a different email address
            to register with Phabricator then you will need to
            ensure the latest commit on your branch uses the
            correct email address.

            You can view your email address like so:

                $ git config --global user.email

            and set it like so:

                $ git config --global user.email "name@server.test"

            If you only want to change your email address
            for the git repo you are currently in, then
            drop the '--global' bit:

                $ git config user.email "name@server.test"

            You should push the branches again but with
            a commit that use the right email address.
            The no-fuss way to do this is the following:

                $ git checkout {branch}
                $ git commit --reuse-message=HEAD --reset-author --allow-empty
                $ git push origin {branch}

            This will copy the message from the last commit
            on the branch and create a new, empty commit
            with the new authorship information.
        """).format(
            repo=self._repository_name,
            branch=branch_name,
            base_branch=branch_base,
            emails=str(emails),
            uri=self._uri
        )
        to = []
        to.extend(self._admin_emails)
        to.extend(emails)
        self._mail_sender.send(
            to_addresses=to,
            subject="user exception",
            message=msg)


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
