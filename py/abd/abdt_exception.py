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
#   ReviewAbandonedException
#   NoHistoryException
#   NoDiffException
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


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


class ReviewAbandonedException(AbdUserException):

    def __init__(self):
        """Describe the situation of a review being abandoned by the author."""
        message = "abdt_exception__ReviewAbandonedException"
        super(ReviewAbandonedException, self).__init__(message)


class NoHistoryException(AbdUserException):

    def __init__(self, review_branch_name, base_name):
        """Describe a review having no commits beyond base.

        :review_branch_name: the string name of the review branch
        :base_name: the string name of the branch the review lands on

        """
        message = "abdt_exception__NoHistoryException"
        super(NoHistoryException, self).__init__(message)
        self.review_branch_name = review_branch_name
        self.base_name = base_name


class NoDiffException(AbdUserException):

    def __init__(self, base_name, review_branch_name, review_branch_hash):
        """Describe a review having no difference against it's base.

        :base_name: the string name of the branch the review lands on
        :review_branch_name: the string name of the review branch
        :review_branch_hash: the string commit hash of the review branch

        """
        message = "abdt_exception__NoDiffException"
        super(NoDiffException, self).__init__(message)
        self.base_name = base_name
        self.review_branch_name = review_branch_name
        self.review_branch_hash = review_branch_hash


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
