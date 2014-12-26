"""Wrapper to call Phabricator's Paste Conduit API."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlcon_paste
#
# Public Functions:
#   create_paste
#
# Public Assignments:
#   CreatePasteResponse
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import phlsys_namedtuple


CreatePasteResponse = phlsys_namedtuple.make_named_tuple(
    'CreatePasteResponse',
    required=[
        'id', 'phid', 'authorPHID', 'filePHID', 'title', 'parentPHID',
        'dateCreated', 'language', 'objectName', 'uri', 'content'
    ],
    defaults={},
    ignored=[])


def create_paste(conduit, content, title="", language=""):
    """Creates a paste in Phabricator.

    :conduit: conduit to operate on
    :content: the content of the paste
    :title: the title of the paste
    :language: the programming language of the paste ie. c++
    :returns: pasteResponse named tuple

    """
    response = conduit(
        "paste.create",
        {"content": content, "title": title, "language": language})
    return CreatePasteResponse(**response)

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
