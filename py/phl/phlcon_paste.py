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
    response = conduit.call(
        "paste.create",
        {"content": content, "title": title, "language": language})
    return CreatePasteResponse(**response)

#------------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
