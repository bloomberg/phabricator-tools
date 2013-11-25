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


def create_task(conduit, title, description="", priority=None):
    """Create a new Maniphest task using the supplied 'conduit'.

    :conduit: supports call()
    :title: string title of the new task
    :description: string long description of the new task
    :priority: integer priority of the new task (see PRIORITIES)
    :returns: a CreateTaskResponse

    """
    d = {
        "title": title,
        "description": description,
    }
    if priority is not None:
        d['priority'] = priority
    response = conduit.call("maniphest.createtask", d)
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
