"""Callables for re-integrating branches upstream.

This component provides a number of 'landers', which will re-integrate a
feature branch back into the current branch, which is assumed to be upstream.

In other words, the 'landers' land a supplied branch on the current branch.

Landers have the interface:
    def lander(repo, feature, author_name, author_email, message)

On success the lander will return a string summary of the landing operation
for a human to review.

If the lander fails to land then it will raise a LanderException with details
of the failure.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_lander
#
# Public Classes:
#   LanderException
#
# Public Functions:
#   squash
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function

import phlgit_merge


class LanderException(Exception):

    def __init__(self, description):
        super(LanderException, self).__init__(description)


def squash(repo, source, author_name, author_email, message):
    """Return the string output of squashing 'source' into current branch."""
    try:
        result = repo.squash_merge(
            source,
            message,
            author_name,
            author_email)
    except phlgit_merge.MergeException as e:
        raise LanderException(e)

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
