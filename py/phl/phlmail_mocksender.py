# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
#
# Public Classes:
#   MailSender
#
# Public Assignments:
#   Mail
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import collections
import types

Mail = collections.namedtuple(
    'phlmail_mocksender__Mail',
    ['subject', 'message', 'to_addresses', 'cc_addresses'])


class MailSender(object):

    """A mail sender that just stores mail to make testing easier."""

    def __init__(self):
        """Setup to store sent email."""
        self._mailboxes = collections.defaultdict(list)
        self._mails = []

    def send(self, subject, message, to_addresses, cc_addresses=None):
        assert not isinstance(to_addresses, types.StringTypes)
        assert not isinstance(cc_addresses, types.StringTypes)
        mail = Mail(subject, message, to_addresses, cc_addresses)
        for address in to_addresses:
            self._mailboxes[address].append(mail)
        if cc_addresses is not None:
            for address in cc_addresses:
                self._mailboxes[address].append(mail)
        self._mails.append(mail)

    @property
    def mailboxes(self):
        return self._mailboxes

    @property
    def mails(self):
        return self._mails


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
