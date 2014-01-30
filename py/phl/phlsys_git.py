"""Wrapper to call git, with working directory."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_git
#
# Public Classes:
#   Repo
#    .call
#    .working_dir
#
# Public Functions:
#   tmprepo_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import os

import phlsys_fs
import phlsys_subprocess


@contextlib.contextmanager
def tmprepo_context():
    """Return a newly created Repo, remove when expired.

    Usage examples:

        Create a temporary repo:
        >>> with tmprepo_context() as clone:
        ...     status = clone.call("rev-parse", "--is-inside-work-tree")
        ...     status.strip().lower() == 'true'
        True

    """
    with phlsys_fs.tmpdir_context() as tmpdir:
        clone = Repo(tmpdir)
        clone.call("init")
        yield clone


# TODO: add support for user.name and user.email to git clone
class Repo(object):

    def __init__(self, workingDir):
        self._workingDir = os.path.abspath(workingDir)

    # def call(*args, stdin=None): <-- supported in Python 3
    def call(self, *args, **kwargs):
        stdin = kwargs.pop("stdin", None)
        assert(not kwargs)
        result = phlsys_subprocess.run(
            'git', *args,
            stdin=stdin, workingDir=self._workingDir)
        return result.stdout

    @property
    def working_dir(self):
        return self._workingDir


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
