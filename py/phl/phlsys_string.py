"""String utility functions."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_string
#
# Public Functions:
#   after_prefix
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def after_prefix(string, prefix):
    """Return 'string' with 'prefix' removed.

    If 'string' does not start with 'prefix' then None is returned.

    Usage examples:

    >>> after_prefix('dog/cat/', 'dog/')
    'cat/'

    >>> after_prefix('dog/cat/', 'mouse/')

    :string: string to operate on
    :prefix: string prefix to remove
    :returns: string representing 'string' with 'prefix' removed or None

    """
    if string.startswith(prefix):
        return string[len(prefix):]
    return None


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
