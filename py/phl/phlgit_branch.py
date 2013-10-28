"""Wrapper around 'git branch'."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_branch
#
# Public Functions:
#   is_tree_same
#   is_identical
#   get_local
#   get_local_with_sha1
#   get_remote
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import


def _cat_file_pretty(clone, objectHash):
    return clone.call('cat-file', '-p', objectHash)


def _get_tree(clone, commit):
    content = _cat_file_pretty(clone, commit).splitlines()
    tree = content[0].split("tree ")[1].strip()
    return tree


def is_tree_same(clone, branch, targetBranch):
    branchTree = _get_tree(clone, branch)
    targetTree = _get_tree(clone, targetBranch)
    return branchTree == targetTree


def _git_rev_parse(clone, rev):
    return clone.call('rev-parse', rev)


def is_identical(clone, branch, targetBranch):
    branchRev = _git_rev_parse(clone, branch)
    targetRev = _git_rev_parse(clone, targetBranch)
    return branchRev == targetRev


def _get_refs(clone):
    # the output list is like:
    #     SHA1      Refname
    #     SHA1      Refname
    #     SHA1      Refname
    out = clone.call('show-ref')
    flat = out.split()  # convert to ['SHA1', 'Refname', 'SHA1', 'Refname']

    # convert to [Refname, Refname, Refname]
    refs = [flat[i + 1] for i in range(0, len(flat) - 1, 2)]
    return refs


def _get_sha1_ref_pairs(clone):
    # the output list is like:
    #     SHA1      Refname
    #     SHA1      Refname
    #     SHA1      Refname
    out = clone.call('show-ref')
    flat = out.split()  # convert to ['SHA1', 'Refname', 'SHA1', 'Refname']

    # convert to [('SHA1', 'Refname'), ('SHA1', 'Refname')]
    refs = [(flat[i], flat[i + 1]) for i in range(0, len(flat) - 1, 2)]
    return refs


def _filter_refs_in_namespace(refs, namespace):
    return [ref[len(namespace):] for ref in refs if ref.startswith(namespace)]


def _filter_sha1_ref_pairs_in_namespace(refs, namespace):
    ns = namespace
    return [(i[0], i[1][len(ns):]) for i in refs if i[1].startswith(ns)]


def get_local(clone):
    refs = _get_refs(clone)
    return _filter_refs_in_namespace(refs, "refs/heads/")


def get_local_with_sha1(clone):
    """Return a list of (sha1, branch_name) from all the local branches.

    :clone: supports clone.call() for interacting with git
    :returns: a list of branches paired with their hashes

    """
    refs = _get_sha1_ref_pairs(clone)
    refs = _filter_sha1_ref_pairs_in_namespace(refs, "refs/heads/")
    return refs


def get_remote(clone, remote):
    refs = _get_refs(clone)
    remote_head = "refs/remotes/" + remote + "/head"
    refs = [r for r in refs if r != remote_head]
    return _filter_refs_in_namespace(refs, "refs/remotes/" + remote + "/")


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
