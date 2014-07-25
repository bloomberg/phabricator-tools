"""Wrapper around 'git rev-parse'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_revparse
#
# Public Classes:
#   Error
#
# Public Functions:
#   get_sha1_or_none
#   get_sha1
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


class Error(Exception):
    pass


def get_sha1_or_none(repo, ref):
    """Return string of the ref's commit hash if valid, else None.

    :repo: a callable supporting git commands, e.g. repo("status")
    :ref: string of the reference to parse
    :returns: string of the ref's commit hash if valid, else None.

    """
    commit = repo("rev-parse", "--revs-only", ref).strip()
    return commit if commit else None


def get_sha1(repo, ref):
    """Return string of the ref's commit hash.

    Raise if the ref is invalid.

    :repo: a callable supporting git commands, e.g. repo("status")
    :ref: string of the reference to parse
    :returns: string of the ref's commit hash

    """
    commit = get_sha1_or_none(repo, ref)
    if commit is None:
        raise Error("ref '{}' is invalid.".format(ref))
    return commit


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
