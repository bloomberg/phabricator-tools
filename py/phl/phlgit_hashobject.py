"""Wrapper around 'git hash-object'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_hashobject
#
# Public Functions:
#   write_string
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def write_string(repo, s):
    """Return the hash of the supplied string 's' and write the object.

    Note that if an object with the same hash (should be the same content) is
    already in the object store then nothing will be written.  The hash will
    still be returned.

    Note that the hash returned is that of (<some header> + s) so you will not
    get the same result if you simply did:
        hashlib.sha1(s)

    :repo: a callable supporting git commands, e.g. repo("status")
    :s: the string to calculate the SHA1 of and to write to the object store
    :returns: the SHA1 of the object

    """
    return repo('hash-object', '-w', '--stdin', stdin=s).strip()


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
