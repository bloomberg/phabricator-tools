"""Wrapper to call Phabricator's Project Conduit API."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_project
#
# Public Functions:
#   query_some
#   query_all
#   make_project_to_phid_dict
#
# Public Assignments:
#   QueryResponse
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlsys_namedtuple


QueryResponse = phlsys_namedtuple.make_named_tuple(
    'QueryResponse',
    required=['name', 'phid'],
    defaults={},
    ignored=['dateCreated', 'members', 'dateModified', 'id'])


def query_some(conduit, max_items, offset):
    """Return a list of some projects from the supplied conduit.

    :conduit: supports call()
    :max_items: the maximum number of items to return
    :offset: the offset into the list of all possible items
    :returns: a list of QueryResponse

    """
    d = {
        'limit': max_items,
        'offset': offset,
    }
    response = conduit.call("project.query", d)
    results = [QueryResponse(**r) for phid, r in response.iteritems()]
    return results


def query_all(conduit):
    """Return a list of all projects from the supplied conduit.

    :conduit: supports call()
    :returns: a list of QueryResponse

    """
    window_size = 5000
    items = query_some(conduit, window_size, 0)
    count = 1
    while len(items) == window_size * count:
        items += query_some(conduit, window_size, window_size * count)
        count += 1
    return items


def make_project_to_phid_dict(conduit):
    """Return a name->phid dictionary of all projects from 'conduit'.

    :conduit: supports call()
    :returns: a dict mapping from project name to project phid

    """
    return {i.name: i.phid for i in query_all(conduit)}


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
