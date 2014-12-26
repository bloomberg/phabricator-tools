"""A mail sender that just stores mail to make testing easier."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlmail_mocksender
#
# Public Classes:
#   MailSender
#    .send
#    .mailboxes
#    .mails
#    .is_empty
#
# Public Assignments:
#   Mail
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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

    def is_empty(self):
        return not self._mails

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
