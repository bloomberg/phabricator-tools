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

from __future__ import print_function
from __future__ import absolute_import

import phlsys_namedtuple


QueryResponse = phlsys_namedtuple.make_named_tuple(
    'QueryResponse',
    required=['name', 'phid'],
    defaults={},
    ignored=['dateCreated', 'members', 'dateModified', 'id', 'slugs'])


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
    response = conduit("project.query", d)

    # the new version of the API stores the items under the 'data' key
    data = response['data'] if 'data' in response else response

    results = [QueryResponse(**r) for phid, r in data.iteritems()]
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


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
