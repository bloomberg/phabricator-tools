""""A global list of error identifiers that may be used.

The identifiers are gathered here for easy reference, for example when
writing an external error logger then it may be useful to know what
kinds of error identifiers to expect.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_errident
#
# Public Assignments:
#   CONDUIT_REFRESH
#   GIT_SNOOP
#   FETCH_PRUNE
#   CONDUIT_CONNECT
#   PUSH_DELETE_REVIEW
#   PUSH_DELETE_TRACKING
#   MARK_BAD_LAND
#   MARK_BAD_ABANDONED
#   MARK_BAD_IN_REVIEW
#   MARK_NEW_BAD_IN_REVIEW
#   MARK_BAD_PRE_REVIEW
#   MARK_OK_IN_REVIEW
#   MARK_OK_NEW_REVIEW
#   PUSH_DELETE_LANDED
#   PUSH_LANDING_ARCHIVE
#   PUSH_ABANDONED_ARCHIVE
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

#
# tryloop identifiers
#

# abdi_processrepos
CONDUIT_REFRESH = "conduit-refresh"
GIT_SNOOP = "git-snoop"

# abdi_processargs
FETCH_PRUNE = 'fetch-prune'
CONDUIT_CONNECT = 'conduit-connect'

# abdt_branch
PUSH_DELETE_REVIEW = 'push-delete-review'
PUSH_DELETE_TRACKING = 'push-delete-tracking'
MARK_BAD_LAND = 'mark-bad-land'
MARK_BAD_ABANDONED = 'mark-bad-abandoned'
MARK_BAD_IN_REVIEW = 'mark-bad-in-review'
MARK_NEW_BAD_IN_REVIEW = 'mark-new-bad-in-review'
MARK_BAD_PRE_REVIEW = 'mark-bad-pre-review'
MARK_OK_IN_REVIEW = 'mark-ok-in-review'
MARK_OK_NEW_REVIEW = 'mark-ok-new-review'
PUSH_DELETE_LANDED = 'push-delete-landed'
PUSH_LANDING_ARCHIVE = 'push-landing-archive'
PUSH_ABANDONED_ARCHIVE = 'push-abandoned-archive'


#------------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
