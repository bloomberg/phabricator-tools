"""Utilities for working with git refs."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgitu_ref
#
# Public Classes:
#   Error
#
# Public Functions:
#   guess_fq_name
#   make_remote
#   make_local
#   fq_remote_to_short_local
#   fq_to_short
#   is_under_remote
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


class Error(Exception):
    pass


def guess_fq_name(name_to_guess_from, remote_list=None):
    """Return a best-guess of the fq name of a ref, given a list of remotes.

    The list of remotes defaults to ['origin'] if None is supplied.

    Usage examples:
        >>> guess_fq_name('master')
        'refs/heads/master'

        >>> guess_fq_name('origin/master')
        'refs/remotes/origin/master'

        >>> guess_fq_name('refs/notes')
        'refs/notes'

    :name_to_guess_from: string name of the ref
    :remote_list: list of string names of remotes

    """
    if not name_to_guess_from:
        raise Error("empty name to guess from")

    if name_to_guess_from.startswith('refs/'):
        return name_to_guess_from

    if remote_list is None:
        remote_list = ['origin']

    for r in remote_list:
        if name_to_guess_from.startswith(r + '/'):
            return "refs/remotes/{}".format(name_to_guess_from)

    return "refs/heads/{}".format(name_to_guess_from)


def make_remote(ref, remote):
    """Return a Git reference based on a local name and a remote name.

    Usage example:
        >>> make_remote("mywork", "origin")
        'refs/remotes/origin/mywork'

        >>> make_remote("mywork", "github")
        'refs/remotes/github/mywork'

    """
    return "refs/remotes/" + remote + "/" + ref


def make_local(ref):
    """Return a fully qualified Git reference based on a local name.

    Usage example:
        >>> make_local("mywork")
        'refs/heads/mywork'

    """
    # TODO: check that it isn't already fully qualified
    return "refs/heads/" + ref


def fq_remote_to_short_local(ref):
    """Return a short Git branch name based on a fully qualified remote branch.

    Raise Error if the conversion can't be done.

    Usage example:
        >>> fq_remote_to_short_local("refs/remotes/origin/mywork")
        'mywork'

        >>> fq_remote_to_short_local("refs/heads/mywork")
        Traceback (most recent call last):
        Error: ref can't be converted to short local: mywork

    """
    # convert to e.g. 'origin/mywork'
    ref = fq_to_short(ref)

    slash_pos = ref.find('/')

    if slash_pos == -1:
        raise Error("ref can't be converted to short local: {}".format(ref))

    # disregard before and including the first slash
    return ref[slash_pos + 1:]


def fq_to_short(ref):
    """Return a short Git reference based on a fully qualified name.

    Raise Error if the conversion can't be done.

    Usage example:
        >>> fq_to_short("refs/heads/mywork")
        'mywork'

        >>> fq_to_short("refs/remotes/origin/mywork")
        'origin/mywork'

    """
    refs_heads = 'refs/heads/'
    refs_remotes = 'refs/remotes/'

    if ref.startswith(refs_heads):
        return ref[len(refs_heads):]

    if ref.startswith(refs_remotes):
        return ref[len(refs_remotes):]

    raise Error("ref can't be converted to short: {}".format(ref))


def is_under_remote(ref, remote):
    """Return True if a Git reference is from a particular remote, else False.

    Note that behavior is undefined if the ref is not fully qualified, i.e.
    does not begin with 'refs/'.

    Usage example:
        >>> is_under_remote("refs/remotes/origin/mywork", "origin")
        True

        >>> is_under_remote("refs/remotes/origin/mywork", "alt")
        False

        >>> is_under_remote("refs/headsmywork", "origin")
        False

    """
    return ref.startswith('refs/remotes/' + remote + '/')



#------------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
