"""Abstraction for Arcyd's conduit operations.

Intended to be a full replacement for phlsys_conduit in Arcyd code, providing
high-level functions for operations.

Until we've replace all existing Conduit.call() calls then we need to duplicate
that functionality too.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_conduit
#
# Public Classes:
#   Conduit
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import phlcon_differential


class Conduit(object):
    def __init__(self, conduit):
        """Initialise a new Conduit.

        :conduit: a phlsys_conduit to delegate to
        :returns: None

        """
        super(Conduit, self).__init__()
        self._conduit = conduit

    def create_comment(self, revision, message, silent=False):
        """Make a comment on the specified 'revision'.

        :revision: id of the revision to comment on
        :message: the string message to leave as a comment, may be empty
        :silent: mail notifications won't be sent if False
        :returns: None

        """
        phlcon_differential.create_comment(
            self._conduit, revision, message, silent=silent)

    def create_revision(self, raw_diff, fields):
        """Return the id of a newly created revision based on specified args.

        See phlcon_differential.MessageFields for some examples of valid input
        for specified 'fields'.

        :raw_diff: raw output string from e.g. 'git diff master...'
        :fields: dict of string attributes, required: 'title' and 'testPlan'
        :returns: id of created revision

        """
        diffid = phlcon_differential.create_raw_diff(
            self._conduit, raw_diff).id
        review = phlcon_differential.create_revision(
            self._conduit, diffid, fields)
        return review.revisionid

    def update_revision(self, revisionid, raw_diff, message):
        """Update an existing Differential revision with a new diff.

        :revisionid: id of the Differential revision to update
        :raw_diff: raw output string from e.g. 'git diff master...'
        :message: string message to annotate the update event with
        :returns: None

        """
        diffid = phlcon_differential.create_raw_diff(
            self._conduit, raw_diff).id
        phlcon_differential.update_revision(
            self._conduit, revisionid, diffid, [], message)

    # XXX: until we replace all usage of phlsys_conduit, delegate missing
    #      functionality to it using getattr and setattr

    def __getattr__(self, attr):
        return getattr(self._conduit, attr)


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
