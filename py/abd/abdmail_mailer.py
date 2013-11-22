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
