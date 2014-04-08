"""Wrapper around 'git show'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_show
#
# Public Functions:
#   object_
#   file_on_ref
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


def object_(repo, ref):
    """Return the content of the specified object.

    :repo: a callable supporting git commands, e.g. repo("status")
    :ref: the ref of the object, e.g. 'origin/master', 'ed3a1', etc.
    :returns: the contents of the object

    """
    return repo('show', ref)


def file_on_ref(repo, path, ref):
    """Return the content of the file at specified 'path' on branch 'ref'.

    Raise if the file or ref does not exist.

    :repo: a callable supporting git commands, e.g. repo("status")
    :path: the string path to the file on the branch, e.g. 'src/main.cpp'
    :ref: the string ref of the branch, e.g. 'feature/red_button'
    :returns: the string contents of the file

    """
    return repo('show', '{}:{}'.format(ref, path))


# -----------------------------------------------------------------------------
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
# ------------------------------ END-OF-FILE ----------------------------------
