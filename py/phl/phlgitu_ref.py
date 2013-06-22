"""Utilities for working with git refs."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgitu_ref
#
# Public Functions:
#   makeRemote
#   makeLocal
#   parseRefHash
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================


def makeRemote(ref, remote):
    """Return a Git reference based on a local name and a remote name.

    Usage example:
        >>> makeRemote("mywork", "origin")
        'refs/remotes/origin/mywork'

        >>> makeRemote("mywork", "github")
        'refs/remotes/github/mywork'
    """
    return str("refs/remotes/" + remote + "/" + ref)


def makeLocal(ref):
    """Return a fully qualified Git reference based on a local name.

    Usage example:
        >>> makeLocal("mywork")
        'refs/heads/mywork'
    """
    # TODO: check that it isn't already fully qualified
    return str("refs/heads/" + ref)


def parseRefHash(clone, ref):
    """Return string of the ref's commit hash if valid, else None.

    :clone: supports call()
    :ref: the reference to parse
    :returns: string of the ref's commit hash if valid, else None.

    """
    commit = clone.call("rev-parse", "--revs-only", ref)
    return commit if commit else None

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
