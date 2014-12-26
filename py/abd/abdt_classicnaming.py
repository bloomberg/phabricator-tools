"""Branch naming conventions for 'arcyd-review/description/base' style."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_classicnaming
#
# Public Classes:
#   Naming
#    .make_tracker_branch_from_name
#    .make_tracker_branch_name
#    .make_review_branch_from_name
#
# Public Assignments:
#   EXAMPLE_REVIEW_BRANCH_NAME
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import phlsys_string

import abdt_naming


EXAMPLE_REVIEW_BRANCH_NAME = "arcyd-review/{description}/{base}".format(
    description=abdt_naming.EXAMPLE_REVIEW_BRANCH_DESCRIPTION,
    base=abdt_naming.EXAMPLE_REVIEW_BRANCH_BASE)


class Naming(object):

    def __init__(self):
        super(Naming, self).__init__()

        # unfortunately the 'classic' scheme is too high in the namespace
        # hierarchy, it creates it's branches alongside other 'top-level' arcyd
        # branch namespaces
        self._tracking_branch_prefix = abdt_naming.ARCYD_BRANCH_NAMESPACE

        self._review_branch_prefix = 'arcyd-review/'
        self._remote = 'origin'

    def make_tracker_branch_from_name(self, branch_name):
        """Return the WorkingBranch for 'branch_name' or None if invalid.

        Usage example:
            >>> naming = Naming()
            >>> make_branch = naming.make_tracker_branch_from_name
            >>> make_branch('dev/arcyd/ok/mywork/master/99')
            ... # doctest: +NORMALIZE_WHITESPACE
            abdt_naming.TrackerBranch("dev/arcyd/ok/mywork/master/99")

            >>> make_branch('dev/arcyd/trackers/x/ok/r/master/do/99')
            Traceback (most recent call last):
                ...
            Error

            >>> make_branch('invalid/mywork/master')
            Traceback (most recent call last):
                ...
            Error

        :branch_name: string name of the working branch
        :returns: WorkingBranch or None if invalid

        """
        if branch_name == abdt_naming.RESERVED_BRANCH_NAME:
            raise abdt_naming.Error()  # ignore the reserved branch

        if branch_name.startswith(abdt_naming.TRACKING_BRANCH_PREFIX):
            raise abdt_naming.Error()  # ignore all new tracker branches

        suffix = phlsys_string.after_prefix(
            branch_name, self._tracking_branch_prefix)

        if not suffix:
            # review branches must start with the prefix
            raise abdt_naming.Error()

        # suffix should be status/description/base(/...)/id
        #                    0   /     1     /  2 (/...)/-1

        parts = suffix.split("/")
        if len(parts) < 4:
            raise abdt_naming.Error()

        description = parts[1]
        base = '/'.join(parts[2:-1])

        review_branch = self._review_branch_prefix
        review_branch += description
        review_branch += "/" + base

        return abdt_naming.TrackerBranch(
            naming=self,
            branch=branch_name,
            review_branch=review_branch,
            status=parts[0],
            description=description,
            base=base,
            rev_id=parts[-1],
            remote=self._remote)

    def make_tracker_branch_name(self, status, description, base, review_id):
        """Return the unique string name of the tracker branch for params.

        Working branches are of the form:
            <working branch prefix>/description/base

        Usage example:
            >>> naming = Naming()
            >>> make_name = naming.make_tracker_branch_name
            >>> make_name('ok', 'mywork', 'master',  99)
            'dev/arcyd/ok/mywork/master/99'

        :description: string descriptive name of the branch
        :base: string name of the branch to diff against and land on
        :id: identifier for the review, converted to str() for convenience
        :returns: string name of the working branch

        """
        tracker_branch = ""
        tracker_branch += self._tracking_branch_prefix
        tracker_branch += status
        tracker_branch += "/" + description
        tracker_branch += "/" + base
        tracker_branch += "/" + str(review_id)
        return tracker_branch

    def make_review_branch_from_name(self, branch_name):
        """Return the ReviewBranch for 'branch_name' or None if invalid.

        Usage example:
            >>> naming = Naming()
            >>> make_branch = naming.make_review_branch_from_name
            >>> make_branch('arcyd-review/mywork/master')
            ... # doctest: +NORMALIZE_WHITESPACE
            abdt_naming.ReviewBranch("arcyd-review/mywork/master")

            >>> make_branch('invalid/mywork/master')
            Traceback (most recent call last):
                ...
            Error

        :branch_name: string name of the review branch
        :returns: ReviewBranch or None if invalid

        """
        suffix = phlsys_string.after_prefix(
            branch_name, self._review_branch_prefix)
        if not suffix:
            # review branches must start with the prefix
            raise abdt_naming.Error()

        parts = suffix.split("/")
        if len(parts) < 2:
            # suffix should be description/base(/...)
            raise abdt_naming.Error()

        base = '/'.join(parts[1:])

        return abdt_naming.ReviewBranch(
            naming=self,
            branch=branch_name,
            description=parts[0],
            base=base,
            remote=self._remote)


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
