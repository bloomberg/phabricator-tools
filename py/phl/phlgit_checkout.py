"""Wrapper around 'git checkout'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_checkout
#
# Public Functions:
#   new_branch_force_based_on
#   branch
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


def new_branch_force_based_on(clone, new_branch, base):
    """Checkout onto a new branch copy of base, overwite existing branch.

    :clone: the clone to operate on
    :new_branch: the name for the new branch
    :base: the name of the branch to copy
    :returns: None

    """
    clone.call('checkout', '-B', new_branch, base)


def branch(clone, branch):
    """Checkout onto an existing branch.

    Note that the existing branch may be on a remote, in which case a tracking
    branch will be set up.

    :clone: the clone to operate on
    :branch: the string name of the branch
    :returns: None

    """
    clone.call('checkout', branch)


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
