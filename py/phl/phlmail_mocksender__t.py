from __future__ import absolute_import

import unittest

import phlmail_mocksender


class Test(unittest.TestCase):

    def test_empty(self):
        mailsender = phlmail_mocksender.MailSender()
        self.assertEqual(len(mailsender.mailboxes), 0)
        self.assertEqual(len(mailsender.mails), 0)

    def test_oneTo(self):
        mailsender = phlmail_mocksender.MailSender()
        subject = "subject"
        message = "message"
        to = "someone@server.test"
        mailsender.send(subject, message, [to])
        self.assertEqual(len(mailsender.mailboxes), 1)
        self.assertEqual(len(mailsender.mails), 1)
        self.assertEqual(mailsender.mailboxes[to][0], mailsender.mails[0])
        mail = mailsender.mails[0]
        self.assertEqual(mail.subject, subject)
        self.assertEqual(mail.message, message)
        self.assertEqual(mail.to_addresses, [to])
        self.assertIsNone(mail.cc_addresses)


#------------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
