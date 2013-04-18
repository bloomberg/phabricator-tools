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


class AbdUserException(AbdBaseException):
    def __init__(self, message):
        """Base for abd user-triggered exceptions to inherit from.

        :message: the message to report

        """
        message = (
            "abdt_exception__UserException:\n" +
            str(message) + "\n")
        super(AbdUserException, self).__init__(message)


class AbdSystemException(AbdBaseException):
    def __init__(self, message):
        """Base for abd system-triggered exceptions to inherit from.

        :message: the message to report

        """
        message = (
            "abdt_exception__UserException:\n" +
            str(message) + "\n")
        super(AbdSystemException, self).__init__(message)


# TODO: add BadBranchNameException
# TODO: add UnrelatedBaseException
# TODO: add EmptyDiffException
# TODO: add NotPhabricatorUserException


class MissingBaseException(AbdUserException):
    def __init__(self, review_branch_name, base_name):
        """Branch which the review branch is based on does not exist.

        :review_branch_name: name of the branch being reviewed
        :base_name: name of the missing base branch

        """
        message = (
            "abdt_exception__MissingBaseException:\n" +
            "review_branch_name: '" + str(review_branch_name) + "'\n" +
            "base_name: '" + str(base_name) + "'\n")
        super(MissingBaseException, self).__init__(message)
        self.review_branch_name = review_branch_name
        self.base_name = base_name


class NoUsersOnBranchException(AbdUserException):
    def __init__(self, review_branch_name, base_name, emails):
        """Branch does not contain commits by any known users.

        :review_branch_name: name of the branch being reviewed
        :base_name: name of the missing base branch
        :emails: email addresses of authors on the branch

        """
        message = (
            "abdt_exception__NoUsersOnBranchException:\n" +
            "review_branch_name: '" + str(review_branch_name) + "'\n" +
            "base_name: '" + str(base_name) + "'\n" +
            "emails: '" + str(emails) + "'\n")
        super(NoUsersOnBranchException, self).__init__(message)
        self.review_branch_name = review_branch_name
        self.base_name = base_name
        self.emails = emails


class CommitMessageParseException(AbdUserException):

    def __init__(self, errors, fields, digest):
        """Describe failure to create fields suitable for review.

        :errors: errors reported by Phabricator
        :fields: the resulting fields response (if any)
        :digest: a digest of the commit messages

        """
        message = (
            "abdt_exception__CommitMessageParseException:\n" +
            "errors: '" + str(errors) + "'\n" +
            "fields: '" + str(fields) + "'\n" +
            "digest: '" + str(digest) + "'\n")
        super(CommitMessageParseException, self).__init__(message)
        self.errors = errors
        self.fields = fields
        self.digest = digest


class LandingException(AbdUserException):

    def __init__(self, message):
        """Describe failure to land a review.

        :message: any available error message

        """
        new_message = (
            "abdt_exception__LandingException:\n" +
            "message: '" + str(message) + "'")
        super(LandingException, self).__init__(new_message)


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
