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
