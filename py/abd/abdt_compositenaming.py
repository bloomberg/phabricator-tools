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
