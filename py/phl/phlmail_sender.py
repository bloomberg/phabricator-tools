"""A mail sender that sends mail via a configured sendmail."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlmail_sender
#
# Public Classes:
#   MailSender
#    .send
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import phlmail_format


class MailSender(object):

    """A mail sender that sends mail via a configured sendmail."""

    def __init__(self, sendmail, from_email):
        """Setup to send mail with 'sendmail' from 'from_email'.

        :sendmail: the sendmail instance to send with, e.g. a phlsys_sendmail
        :from_email: the address to send from

        """
        self._sendmail = sendmail
        self._from_email = from_email

    def send(self, subject, message, to_addresses, cc_addresses=None):
        mime = phlmail_format.text(
            subject, message, self._from_email, to_addresses, cc_addresses)
        self._sendmail.send(mime)


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
