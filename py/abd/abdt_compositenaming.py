"""Composite multiple naming schemes by chaining them together."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_compositenaming
#
# Public Classes:
#   Naming
#    .make_tracker_branch_from_name
#    .make_review_branch_from_name
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abdt_naming


class Naming(object):

    def __init__(self, *schemes):
        super(Naming, self).__init__()
        assert schemes
        self._schemes = schemes

    def make_tracker_branch_from_name(self, branch_name):
        """Return the WorkingBranch for 'branch_name' or None if invalid.

        :branch_name: string name of the working branch
        :returns: WorkingBranch or None if invalid

        """
        for s in self._schemes:
            try:
                return s.make_tracker_branch_from_name(branch_name)
            except abdt_naming.Error:
                pass  # just try the next scheme if the name is not valid

        # no schemes could convert the name
        raise abdt_naming.Error()

    def make_review_branch_from_name(self, branch_name):
        """Return the ReviewBranch for 'branch_name' or None if invalid.

        :branch_name: string name of the review branch
        :returns: ReviewBranch or None if invalid

        """
        for s in self._schemes:
            try:
                return s.make_review_branch_from_name(branch_name)
            except abdt_naming.Error:
                pass  # just try the next scheme if the name is not valid

        # no schemes could convert the name
        raise abdt_naming.Error()


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
