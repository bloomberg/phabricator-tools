from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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
