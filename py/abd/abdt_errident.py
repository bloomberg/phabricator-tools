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
from __future__ import division
from __future__ import print_function

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
