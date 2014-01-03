"""Wrapper to call Phabricator's Maniphest Conduit API."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_maniphest
#
# Public Functions:
#   create_task
#   update_task
#   query
#
# Public Assignments:
#   PRIORITIES
#   PRIORITY_DESCRIPTIONS
#   PRIORITY_DESCRIPTIONS_TO_VALUES
#   STATUSES
#   STATUS_FILTERS
#   ORDERS
#   CreateTaskResponse
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlsys_namedtuple


# Enumerate the priorities that a Maniphest task may have
# from ManiphestTaskPriority.php
PRIORITIES = {
    'unbreak_now': 100,
    'triage': 90,
    'high': 80,
    'normal': 50,
    'low': 25,
    'wish': 0,
}

# from ManiphestTaskPriority.php
PRIORITY_DESCRIPTIONS = {
    PRIORITIES['unbreak_now']: 'Unbreak Now!',
    PRIORITIES['triage']: 'Needs Triage',
    PRIORITIES['high']: 'High',
    PRIORITIES['normal']: 'Normal',
    PRIORITIES['low']: 'Low',
    PRIORITIES['wish']: 'Wishlist',
}

# from ManiphestTaskPriority.php
PRIORITY_DESCRIPTIONS_TO_VALUES = {
    desc: val for val, desc in PRIORITY_DESCRIPTIONS.iteritems()
}

# from ManiphestTaskStatus.php
STATUSES = {
    0: 'Open',
    1: 'Resolved',
    2: 'Wontfix',
    3: 'Invalid',
    4: 'Duplicate',
    5: 'Spite',
}

# from ManiphestTaskQuery.php
STATUS_FILTERS = {
    'any': 'status-any',
    'open': 'status-open',
    'closed': 'status-closed',
    'resolved': 'status-resolved',
    'wontfix': 'status-wontfix',
    'invalid': 'status-invalid',
    'spite': 'status-spite',
    'duplicate': 'status-duplicate',
}

# from ManiphestTaskQuery.php
ORDERS = {
    'priority': 'order-priority',
    'created': 'order-created',
    'modified': 'order-modified',
    'title': 'order-title',
}

CreateTaskResponse = phlsys_namedtuple.make_named_tuple(
    'CreateTaskResponse',
    required=[
        'id', 'uri', 'title', 'status', 'priority',
        'authorPHID', 'phid', 'description', 'objectName',
        'auxiliary', 'ccPHIDs', 'ownerPHID', 'dateModified',
        'dateCreated', 'projectPHIDs'
    ],
    defaults={},
    ignored=[])


def create_task(
        conduit,
        title,
        description="",
        priority=None,
        owner=None,
        ccs=None,
        projects=None):
    """Create a new Maniphest task using the supplied 'conduit'.

    :conduit: supports call()
    :title: string title of the new task
    :description: string long description of the new task
    :priority: integer priority of the new task (see PRIORITIES)
    :owner: PHID of the owner or None
    :ccs: PHIDs of the users to cc or None
    :projects: PHIDs of the projects to add to or None
    :returns: a CreateTaskResponse

    """
    d = {
        "title": title,
        "description": description,
    }
    if priority is not None:
        d['priority'] = priority
    if owner is not None:
        d['ownerPHID'] = owner
    if ccs is not None:
        d['ccPHIDs'] = ccs
    if projects is not None:
        d['projectPHIDs'] = projects
    response = conduit.call("maniphest.createtask", d)
    return CreateTaskResponse(**response)


def update_task(
        conduit,
        id,
        title=None,
        description=None,
        priority=None,
        owner=None,
        ccs=None,
        projects=None,
        comment=None):
    """Update a Maniphest task using the supplied 'conduit'.

    :conduit: supports call()
    :id: the id of the task to update
    :title: new string title of the new task or None
    :description: new string long description of the new task or None
    :priority: new integer priority of the new task (see PRIORITIES) or None
    :owner: PHID of the owner or None
    :ccs: PHIDs of the users to cc or None
    :projects: PHIDs of the projects to add to or None
    :comment: string comment to make on the task or None
    :returns: a CreateTaskResponse

    """
    d = {
        "id": id,
    }
    if title is not None:
        d['title'] = title
    if description is not None:
        d['description'] = description
    if priority is not None:
        d['priority'] = priority
    if owner is not None:
        d['ownerPHID'] = owner
    if ccs is not None:
        d['ccPHIDs'] = ccs
    if projects is not None:
        d['projectPHIDs'] = projects
    if comment is not None:
        d['comments'] = comment
    response = conduit.call("maniphest.update", d)
    return CreateTaskResponse(**response)


def query(
        conduit,
        ids=None,
        authors=None,
        owners=None,
        ccs=None,
        projects=None,
        status=None,
        limit=None,
        offset=None,
        order=None,
        text=None):
    """Query Maniphest tasks using the supplied 'conduit'.

    :conduit: supports call()
    :ids: a list of specific task ids to restrict the query to
    :authors: a list of author PHIDs to restrict the query to (any of)
    :owners: a list of owner PHIDs to restrict the query to (any of)
    :ccs: a list of owner PHIDs to restrict the query to (any of)
    :projects: a list of project PHIDs to restrict the query to (any of)
    :status: a particular value of STATUS_FILTERS to apply
    :limit: int limit of results to return, defaults to server value if None
    :offset: int offset into the list of results to return
    :order: one of ORDERS to impose an ordering on results
    :text: string to search tasks for
    :returns: a CreateTaskResponse

    """
    d = {
        'ids': ids,
        'authorPHIDs': authors,
        'ownerPHIDs': owners,
        'ccPHIDs': ccs,
        'projectPHIDs': projects,
        'status': status,
        'limit': limit,
        'offset': offset,
        'order': order,
        'fullText': text,
    }

    response = conduit.call("maniphest.query", d)
    result = []

    if response:
        # oddly we get an empty list instead of a dictionary if no results, so
        # iteritems() isn't appropriate in that case.
        result = [CreateTaskResponse(**v) for k, v in response.iteritems()]

        # order is broken because conduit returns a dict (unordered) instead of
        # a list, we have to impose order here instead, note that it's still
        # important to pass ordering to conduit in case there is a limit on the
        # number of results returned
        priority_desc_to_val = PRIORITY_DESCRIPTIONS_TO_VALUES
        order_to_key = {
            None: lambda x: -int(x.dateModified),
            ORDERS['title']: lambda x: x.title,
            ORDERS['created']: lambda x: -int(x.dateCreated),
            ORDERS['modified']: lambda x: -int(x.dateModified),
            ORDERS['priority']: lambda x: -priority_desc_to_val[x.priority],
        }
        result.sort(key=order_to_key[order])

    return result

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
