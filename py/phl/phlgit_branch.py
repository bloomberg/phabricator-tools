"""Wrapper around 'git branch'"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgit_branch
#
# Public Functions:
#   isTreeSame
#   isIdentical
#   getLocal
#   getRemote
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================


def _catFilePretty(clone, objectHash):
    return clone.call('cat-file', '-p', objectHash)


def _getTree(clone, commit):
    content = _catFilePretty(clone, commit).splitlines()
    tree = content[0].split("tree ")[1].strip()
    return tree


def isTreeSame(clone, branch, targetBranch):
    branchTree = _getTree(clone, branch)
    targetTree = _getTree(clone, targetBranch)
    return branchTree == targetTree


def _gitRevParse(clone, rev):
    return clone.call('rev-parse', rev)


def isIdentical(clone, branch, targetBranch):
    branchRev = _gitRevParse(clone, branch)
    targetRev = _gitRevParse(clone, targetBranch)
    return branchRev == targetRev


def _getRefs(clone):
    # the output list is like:
    #     SHA1      Refname
    #     SHA1      Refname
    #     SHA1      Refname
    out = clone.call('show-ref')
    flat = out.split()  # convert to ['SHA1', 'Refname', 'SHA1', 'Refname']
    # convert to [Refname, Refname, Refname]
    refs = [flat[i + 1] for i in range(0, len(flat) - 1, 2)]
    return refs


def _filterRefsInNamespace(refs, namespace):
    return [ref[len(namespace):] for ref in refs if ref.startswith(namespace)]


def getLocal(clone):
    refs = _getRefs(clone)
    return _filterRefsInNamespace(refs, "refs/heads/")


def getRemote(clone, remote):
    refs = _getRefs(clone)
    remote_head = "refs/remotes/" + remote + "/head"
    refs = [r for r in refs if r != remote_head]
    return _filterRefsInNamespace(refs, "refs/remotes/" + remote + "/")


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
