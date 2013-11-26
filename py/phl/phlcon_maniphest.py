"""Wrapper to call Phabricator's Maniphest Conduit API."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_maniphest
#
# Public Functions:
#   create_task
#
# Public Assignments:
#   PRIORITIES
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

CreateTaskResponse = phlsys_namedtuple.make_named_tuple(
    'CreateTaskResponse',
    required=['id', 'uri'],
    defaults={},
    ignored=[
        'authorPHID', 'status', 'phid', 'description', 'objectName', 'title',
        'auxiliary', 'ccPHIDs', 'priority', 'ownerPHID', 'dateModified',
        'dateCreated', 'projectPHIDs'
    ])


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
