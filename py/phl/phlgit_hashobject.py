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


def write_string(clone, s):
    """Return the hash of the supplied string 's' and write the object.

    Note that if an object with the same hash (should be the same content) is
    already in the object store then nothing will be written.  The hash will
    still be returned.

    Note that the hash returned is that of (<some header> + s) so you will not
    get the same result if you simply did:
        hashlib.sha1(s)

    :clone: the git clone to store the object in
    :s: the string to calculate the SHA1 of and to write to the object store
    :returns: the SHA1 of the object

    """
    return clone.call('hash-object', '-w', '--stdin', stdin=s).strip()


#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#------------------------------- END-OF-FILE ----------------------------------
