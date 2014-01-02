"""Branch naming conventions for 'r/base/description' style."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_rbranchnaming
#
# Public Classes:
#   Naming
#    .make_tracker_branch_from_name
#    .make_tracker_branch_name
#    .make_review_branch_from_name
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlsys_string

import abdt_naming


class Naming(object):

    """A naming scheme to support 'r/master/change' style branches.

    review branches are composed like this:

       r/master/somedescription
       1|  2   |       3

       1 - prefix for review branches to distinguish from feature/bugfix etc.
       2 - 'base' - variable number of slashes, the name of the branch to diff
           the review branch against and to land the review branch on to.
       3 - 'description' - a short-hand label for the branch for humans, could
           be something like 'fix_startup_crash', 'ci_support_T39891', etc.

    See doc/design/r_branch_naming_scheme.txt for full details.

    the corresponding tracker branches are composed like this:

         dev/arcyd/trackers/rbranch/--/-/ok/r/master/somedescription/99
        |         1        |    2  | 3|4| 5|          6             | 7|

        1 - a namespace for all tracking branches
        2 - a namespace for this scheme
        3 - reserved for version number of this scheme
        4 - a reserved section, probably for supporting multiple conduit URLs
        5 - the status of the branch
        6 - the full name of the original review branch (variable slashes)
        7 - the id of the review, or 'none' if there is no associated review

    """

    def __init__(self):
        super(Naming, self).__init__()
        self._tracking_branch_prefix = 'dev/arcyd/trackers/rbranch/--/-/'
        self._reserve_branch_prefix = 'dev/arcyd/reserve'
        self._review_branch_prefix = 'r/'
        self._remote = 'origin'

    def make_tracker_branch_from_name(self, branch_name):
        """Return the WorkingBranch for 'branch_name' or None if invalid.

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

        # suffix should be status/r/base(/...)/description/id
        #                       0/1/  2 (/...)/    -2     /-1

        parts = suffix.split("/")
        if len(parts) < 5:
            # suffix should be status/base(/...)/description/id
            raise abdt_naming.Error()

        review_prefix = parts[1] + '/'
        if review_prefix != self._review_branch_prefix:
            # doesn't begin with our review branch prefix
            raise abdt_naming.Error()

        base = '/'.join(parts[2:-2])
        review_branch = '/'.join(parts[1:-1])

        return abdt_naming.TrackerBranch(
            naming=self,
            branch=branch_name,
            review_branch=review_branch,
            status=parts[0],
            base=base,
            description=parts[-2],
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
            'dev/arcyd/trackers/rbranch/--/-/ok/r/master/mywork/99'

        :description: string descriptive name of the branch
        :base: string name of the branch to diff against and land on
        :id: identifier for the review, converted to str() for convenience
        :returns: string name of the working branch

        """
        tracker_branch = ""
        tracker_branch += self._tracking_branch_prefix
        tracker_branch += status + "/"
        tracker_branch += self._review_branch_prefix
        tracker_branch += base + "/"
        tracker_branch += description + "/"
        tracker_branch += str(review_id)
        return tracker_branch

    def make_review_branch_from_name(self, branch_name):
        """Return the ReviewBranch for 'branch_name' or None if invalid.

        Usage example:
            >>> naming = Naming()
            >>> make_branch = naming.make_review_branch_from_name
            >>> make_branch('r/master/mywork')
            ... # doctest: +NORMALIZE_WHITESPACE
            abdt_naming.ReviewBranch("r/master/mywork")

            >>> make_branch('invalid/master/mywork')
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

        base = '/'.join(parts[0:-1])

        return abdt_naming.ReviewBranch(
            naming=self,
            branch=branch_name,
            description=parts[-1],
            base=base,
            remote=self._remote)


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
