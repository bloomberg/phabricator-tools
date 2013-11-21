"""Exception hierarchy for abd user and system errors."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_exception
#
# Public Classes:
#   AbdBaseException
#   AbdUserException
#   AbdSystemException
#   MissingBaseException
#   NoUsersOnBranchException
#   LargeDiffException
#   CommitMessageParseException
#   LandingException
#   LandingPushBaseException
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


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

    def __init__(self, review_branch_name, description, base_name):
        """Branch which the review branch is based on does not exist.

        :review_branch_name: name of the branch being reviewed
        :description: description part of the branch
        :base_name: name of the missing base branch

        """
        message = (
            "abdt_exception__MissingBaseException:\n" +
            "review_branch_name: '" + str(review_branch_name) + "'\n" +
            "description: '" + str(description) + "'\n" +
            "base_name: '" + str(base_name) + "'\n")
        super(MissingBaseException, self).__init__(message)
        self.review_branch_name = review_branch_name
        self.description = description
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


class LargeDiffException(AbdUserException):

    def __init__(self, diff_summary, diff_len, diff_len_limit):
        """Describe failure to create small enough diff.

        :diff_summary: a textual summary of the diff, e.g. diff --stat
        :diff_len: the size of the diff
        :diff_len_limit: the size limit for diffs

        """
        message = (
            "abdt_exception__LargeDiffException:\n"
            "diff_summary: '" + str(diff_summary) + "'\n"
            "diff_len: '" + str(diff_len) + "'\n"
            "diff_len_limit: '" + str(diff_len_limit) + "'\n")
        super(LargeDiffException, self).__init__(message)
        self.diff_summary = diff_summary
        self.diff_len = diff_len
        self.diff_len_limit = diff_len_limit


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

    def __init__(self, message, review_branch_name, base_name):
        """Describe failure to land a review.

        :message: any available error message
        :review_branch_name: name of the branch being reviewed
        :base_name: name of the base branch

        """
        new_message = (
            "abdt_exception__LandingException:\n" +
            "message: '" + str(message) + "'\n" +
            "review_branch_name: '" + str(review_branch_name) + "'\n" +
            "base_name: '" + str(base_name) + "'\n")
        super(LandingException, self).__init__(new_message)
        self.review_branch_name = review_branch_name
        self.base_name = base_name


class LandingPushBaseException(AbdUserException):

    def __init__(self, message, review_branch_name, base_name):
        """Describe failure to land a review at the push new base stage.

        :message: any available error message
        :review_branch_name: name of the branch being reviewed
        :base_name: name of the base branch

        """
        new_message = (
            "abdt_exception__LandingPushBaseException:\n" +
            "message: '" + str(message) + "'\n" +
            "review_branch_name: '" + str(review_branch_name) + "'\n" +
            "base_name: '" + str(base_name) + "'\n")
        super(LandingPushBaseException, self).__init__(new_message)
        self.review_branch_name = review_branch_name
        self.base_name = base_name


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
