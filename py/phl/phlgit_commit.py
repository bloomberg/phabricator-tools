"""Dependable wrapper for invocations of git commit."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_commit
#
# Public Functions:
#   index
#   allow_empty
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def index(repo, message):
    """Create a new commit from the contents of the index.

    :repo: a callable supporting git commands, e.g. repo("status")
    :message: the string message for the commit
    :returns: None

    """
    repo('commit', '-m', message)


def allow_empty(repo, message):
    """Create a new commit from the contents of the index, which may be empty.

    :repo: a callable supporting git commands, e.g. repo("status")
    :message: the string message for the commit
    :returns: None

    """
    repo('commit', '--allow-empty', '-m', message)


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
