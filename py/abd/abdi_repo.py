"""Manage git repositories watched by arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_repo
#
# Public Functions:
#   setup_repo
#   setup_repo_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
from __future__ import absolute_import

import contextlib
import shutil

import phlgit_commit
import phlgitx_ignoreident
import phlsys_git
import phlsys_subprocess

import abdt_git


def setup_repo(repo_url, repo_path):
    """Setup a repository, if an exception is raised then remove the repo.

    :repo_url: string url of the repo to clone
    :repo_path: string path to clone the repo to
    :returns: None

    """
    with setup_repo_context(repo_url, repo_path):
        pass


@contextlib.contextmanager
def setup_repo_context(repo_url, repo_path):
    """Setup a repository, if an exception is raised then remove the repo.

    :repo_url: string url of the repo to clone
    :repo_path: string path to clone the repo to
    :returns: None

    """
    # if there's any failure after cloning then we should remove the repo
    phlsys_subprocess.run(
        'git', 'clone', repo_url, repo_path)
    try:
        repo = phlsys_git.Repo(repo_path)

        # make sure we have no problems with 'ident' strings, we won't build
        # from arcyd so it shouldn't be externally visible that we don't expand
        # them.
        phlgitx_ignoreident.ensure_repo_ignoring(repo_path)

        # test pushing to master
        repo('checkout', 'origin/master')
        phlgit_commit.allow_empty(repo, 'test commit for pushing')
        repo('push', 'origin', '--dry-run', 'HEAD:refs/heads/master')
        repo('checkout', '-')

        # test push to special refs
        repo('push', 'origin', '--dry-run', 'HEAD:refs/arcyd/test')
        repo('push', 'origin', '--dry-run', 'HEAD:refs/heads/dev/arcyd/test')

        # fetch the 'landed' and 'abandoned' refs if they exist
        abdt_git.checkout_master_fetch_special_refs(repo, 'origin')

        # success, allow the caller to do work
        yield
    except Exception:
        # clean up the git repo on any exception
        shutil.rmtree(repo_path)
        raise


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
# ------------------------------ END-OF-FILE ----------------------------------
