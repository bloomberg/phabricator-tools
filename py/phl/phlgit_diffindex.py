"""Wrapper around 'git diff-index'.

Compares the content and mode of the blobs found via a tree object with the
content of the current index and, optionally ignoring the stat state of the
file on disk. When paths are specified, compares only those named paths.
Otherwise all entries in the index are compared.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_diffindex
#
# Public Functions:
#   is_index_dirty
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


def is_index_dirty(repo):
    """Return True if there are staged changes, False otherwise.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: Bool

    """
    result = True
    if not repo("diff-index", "--cached", "HEAD", "--name-only"):
        result = False
    return result


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
