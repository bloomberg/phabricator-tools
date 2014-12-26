"""Format valid mime-text suitable for piping into sendmail."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlmail_format
#
# Public Functions:
#   text
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import email.mime.text
import types

# TODO: add support for multipart, including html etc.


# XXX: not really sure we can support bcc in the header so leave it off for now
def text(subject, message, from_address, to_addresses, cc_addresses=None):
    """Return a string of mime-text based on supplied parameters.

    :subject: the string subject line for the message
    :message: the string body of the message
    :from_address: the string email address we are sending from
    :to_addresses: the list of string email addresses we are sending to
    :cc_addresses: the list of string email addresses we are ccing to
    :returns: string mime-text

    """
    assert not isinstance(to_addresses, types.StringTypes), "'to' is string"
    msg = email.mime.text.MIMEText(message)
    msg['subject'] = subject
    msg['from'] = from_address
    msg['to'] = ', '.join(to_addresses)
    if cc_addresses:
        assert not isinstance(cc_addresses, types.StringTypes), "cc is string"
        msg['cc'] = ', '.join(cc_addresses)
    return msg.as_string()


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
