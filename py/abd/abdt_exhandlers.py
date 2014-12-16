"""Factory functions for exception handlers."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_exhandlers
#
# Public Functions:
#   make_exception_message_handler
#   make_exception_delay_handler
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import logging
import platform
import sys
import traceback

import phlmail_sender
import phlsys_sendmail

import abdt_logging


_LOGGER = logging.getLogger(__name__)


def _send_mail(mailsender, emails, uname, subject, tb, body_prefix, message):
    body = uname + "\n" + tb
    body += str(body_prefix)
    body += str(message)
    mailsender.send(
        subject=str(subject),
        message=body,
        to_addresses=emails)


def make_exception_message_handler(
        sys_admin_emails, repo, subject, body_prefix):
    uname = str(platform.uname())
    emails = sys_admin_emails

    mailsender = phlmail_sender.MailSender(
        phlsys_sendmail.Sendmail(),
        "arcyd@" + platform.node())

    def msg_exception(message):
        tb = traceback.format_exc()
        short_tb = traceback.format_exc(1)

        exc_type, _, _ = sys.exc_info()

        _LOGGER.error(
            'abdt_exhandlers: during "{}" encountered exception "{}", '
            'will retry in {}.'.format(
                repo, exc_type.__name__, message),
            exc_info=1)

        detail = ""
        if repo:
            detail += "processing repo: {repo}\n".format(repo=repo)
        detail += "exception: {exception}".format(exception=short_tb)
        abdt_logging.on_system_error('processargs', detail)

        try:
            _send_mail(
                mailsender, emails, uname, subject, tb, body_prefix, message)
        except Exception:
            _LOGGER.error('Exception when sending mail', exc_info=1)

    return msg_exception


def make_exception_delay_handler(sys_admin_emails, repo):
    return make_exception_message_handler(
        sys_admin_emails,
        repo,
        "arcyd paused with exception",
        "will wait: ")


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
