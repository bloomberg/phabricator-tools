"""Wrapper around 'git show-ref'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_showref
#
# Public Functions:
#   names
#   hash_ref_pairs
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function


def names(repo):
    """Return a list of string names of the refs in the supplied repo.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: a list of string names

    """
    result = [name for sha1, name in hash_ref_pairs(repo)]
    return result


def hash_ref_pairs(repo):
    """Return a list of (sha1, name) tuples from the list of refs in 'repo'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: a list of (sha1, name)

    """
    result = [line.split() for line in repo('show-ref').splitlines()]
    return result


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
