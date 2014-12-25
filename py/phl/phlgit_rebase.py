"""Dependable wrapper for invocations of git rebase."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_rebase
#
# Public Functions:
#   onto_upstream
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function


def onto_upstream(repo, upstream):
    """Rebase HEAD onto the supplied 'upstream'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :upstream: the string name of the branch to rebase onto
    :returns: None

    """
    repo('rebase', upstream)


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
