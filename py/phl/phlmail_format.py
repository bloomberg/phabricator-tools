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

import types
from email.mime.text import MIMEText

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
    msg = MIMEText(message)
    msg['subject'] = subject
    msg['from'] = from_address
    msg['to'] = ', '.join(to_addresses)
    if cc_addresses:
        assert not isinstance(cc_addresses, types.StringTypes), "cc is string"
        msg['cc'] = ', '.join(cc_addresses)
    return msg.as_string()


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
