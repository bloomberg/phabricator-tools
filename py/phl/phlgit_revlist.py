"""Wrapper around 'git rev-list'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_revlist
#
# Public Functions:
#   commits
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def commits(repo, *commits):
    """Return list of strings of commit SHA1s reachable from each in 'commits'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :*commits: string names of commits to traverse
    :returns: list of string commit SHA1s

    """
    return repo('rev-list', *commits).splitlines()


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
