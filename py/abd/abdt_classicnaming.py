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
#    .make_review_branch_name
#    .make_review_branch_name_from_tracker
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlsys_string

import abdt_naming


class Naming(object):

    def __init__(self):
        super(Naming, self).__init__()
        self._tracking_branch_prefix = 'dev/arcyd/'
        self._reserve_branch_prefix = 'dev/arcyd/reserve'
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

            >>> make_branch('invalid/mywork/master')
            Traceback (most recent call last):
                ...
            Error

        :branch_name: string name of the working branch
        :returns: WorkingBranch or None if invalid

        """
        if branch_name == self._reserve_branch_prefix:
            raise abdt_naming.Error()  # ignore the reserved branch

        suffix = phlsys_string.after_prefix(
            branch_name, self._tracking_branch_prefix)

        if not suffix:
            # review branches must start with the prefix
            raise abdt_naming.Error()

        parts = suffix.split("/")
        if len(parts) < 4:
            # suffix should be status/description/base(/...)/id
            raise abdt_naming.Error()

        base = '/'.join(parts[2:-1])

        return abdt_naming.TrackerBranch(
            naming=self,
            branch=branch_name,
            status=parts[0],
            description=parts[1],
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

    def make_review_branch_name(self, description, base):
        """Return the unique string name of the review branch for these params.

        Review branches are of the form:
            <review branch prefix>/description/base

        Usage Example:
            >>> naming = Naming()
            >>> make_name = naming.make_review_branch_name
            >>> make_name('mywork', 'master')
            'arcyd-review/mywork/master'

        :description: string descriptive name of the branch
        :base: string name of the branch to diff against and land on
        :returns: string name of the review branch

        """
        branch_name = self._review_branch_prefix
        branch_name += description
        branch_name += "/" + base
        return branch_name

    def make_review_branch_name_from_tracker(self, tracker_branch):
        """Return the string review branch name for 'working_branch'.

        :working_branch: a WorkingBranch
        :returns: the string review branch name for 'working_branch'

        """
        branch_name = self._review_branch_prefix
        branch_name += tracker_branch.description
        branch_name += "/" + tracker_branch.base
        return branch_name


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
