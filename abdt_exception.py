#!/usr/bin/env python
# encoding: utf-8

"""Exception hierarchy for abd user and system errors."""


class AbdBaseException(Exception):
    def __init__(self, message):
        """Base for abd exceptions to inherit from.

        :message: the message to report

        """
        message = (
            "abdt_exception__BaseException:\n" +
            str(message) + "\n")
        super(AbdBaseException, self).__init__(message)


class AbdUserException(Exception):
    def __init__(self, message):
        """Base for abd user-triggered exceptions to inherit from.

        :message: the message to report

        """
        message = (
            "abdt_exception__UserException:\n" +
            str(message) + "\n")
        super(AbdUserException, self).__init__(message)


class AbdSystemException(Exception):
    def __init__(self, message):
        """Base for abd system-triggered exceptions to inherit from.

        :message: the message to report

        """
        message = (
            "abdt_exception__UserException:\n" +
            str(message) + "\n")
        super(AbdSystemException, self).__init__(message)


class InitialCommitMessageParseException(AbdUserException):
    def __init__(self, email, errors, fields, digest):
        """Failure to create suitable message fields before there is a review.

        :email: email address of the user that created the review
        :errors: errors reported by Phabricator
        :fields: the resulting fields response (if any)
        :digest: a digest of the commit messages

        """
        message = (
            "abdcmd_default__CommitMessageParseException:\n" +
            "email: '" + str(email) + "'\n" +
            "errors: '" + str(errors) + "'\n" +
            "fields: '" + str(fields) + "'\n" +
            "digest: '" + str(digest) + "'\n")
        super(InitialCommitMessageParseException, self).__init__(message)
        self._email = email
        self._errors = errors
        self._fields = fields
        self._digest = digest

    @property
    def email(self):
        return self._email


class CommitMessageParseException(AbdUserException):

    def __init__(self, errors, fields, digest):
        """Describe failure to create fields suitable for review.

        :errors: errors reported by Phabricator
        :fields: the resulting fields response (if any)
        :digest: a digest of the commit messages

        """
        message = (
            "abdcmd_default__CommitMessageParseException:\n" +
            "errors: '" + str(errors) + "'\n" +
            "fields: '" + str(fields) + "'\n" +
            "digest: '" + str(digest) + "'\n")
        super(CommitMessageParseException, self).__init__(message)
        self._errors = errors
        self._fields = fields
        self._digest = digest


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
