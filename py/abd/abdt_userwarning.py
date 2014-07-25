"""Hierarchy of warnings to feed back to users."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_userwarning
#
# Public Classes:
#   Base
#   UsedDefaultTestPlan
#   UnknownReviewers
#   SelfReviewer
#   LargeDiff
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


class Base(object):

    def __init__(self, message):
        super(Base, self).__init__()
        self.message = message

    def __repr__(self):
        return 'abdt_userwarning.Warning({})'.format(repr(self.message))


class UsedDefaultTestPlan(Base):

    def __init__(self, default_message):
        super(UsedDefaultTestPlan, self).__init__(
            'used default message: {}'.format(default_message))
        self.default_message = default_message


class UnknownReviewers(Base):

    def __init__(self, unknown_reviewers, commit_message):
        super(UnknownReviewers, self).__init__(
            'some specified reviewers are unknown: {}'.format(
                unknown_reviewers))

        self.unknown_reviewers = unknown_reviewers
        self.commit_message = commit_message


class SelfReviewer(Base):

    def __init__(self, user, commit_message):
        super(SelfReviewer, self).__init__(
            'you cannot review your own change: {}\n{}'.format(
                user, commit_message))

        self.user = user
        self.commit_message = commit_message


class LargeDiff(Base):

    def __init__(self, diff_result):
        super(LargeDiff, self).__init__('large diff')
        self.diff_result = diff_result


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
