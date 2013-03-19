#!/usr/bin/env python
# encoding: utf-8

from email.mime.text import MIMEText


class MailSender(object):
    """A mail sender that just prints the mails to the console."""

    def __init__(self, from_email):
        """Setup to print email to the console from 'from_email'.

        :from_email: the address to send from

        """
        self._from_email = from_email

    def send(self, to, subject, message, cc=None):
        assert not isinstance(to, basestring), "'to' is string"
        msg = MIMEText(message)
        msg['subject'] = subject
        msg['from'] = self._from_email
        msg['to'] = ', '.join(to)
        if cc:
            assert not isinstance(cc, basestring), "cc is string"
            msg['cc'] = ', '.join(cc)
        print "-----"
        print msg.as_string()
        print "-----"


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
