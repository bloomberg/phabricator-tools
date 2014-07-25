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
