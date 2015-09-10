"""Manage git repositories watched by arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_repo
#
# Public Functions:
#   setup_repo
#   setup_repo_context
#   try_push_special_refs
#   is_remote_reserve_branch_present
#   ensure_reserve_branch
#   is_legacy_landinglog_branch_present
#   remove_landinglog
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
import shutil

import phlgit_branch
import phlgit_checkout
import phlgit_commit
import phlgit_push
import phlgitu_ref
import phlgitx_ignoreattributes
import phlsys_git
import phlsys_subprocess

import abdt_git


_RESERVE_BRANCH_FQ_NAME = 'refs/heads/dev/arcyd/reserve'
_LEGACY_LANDINGLOG_NAME = 'refs/arcyd/landinglog'

# The lines in this string are wrapped as appropriate for a commit message
_RESERVE_BRANCH_MESSAGE = """
Reserve the 'dev/arcyd/' branch namespace

This branch is created to reserve the 'dev/arcyd/' namespace so that
arcyd may create it's tracker branches there.

If we didn't do this then it would be possible to create a branch,
e.g.  'dev', which would subsequently stop any 'dev/*' branches
being created.
""".strip()


def setup_repo(repo_url, repo_path, repo_push_url=None):
    """Setup a repository, if an exception is raised then remove the repo.

    :repo_url: string url of the repo to clone
    :repo_path: string path to clone the repo to
    :repo_push_url: string url to push to, or None
    :returns: None

    """
    with setup_repo_context(repo_url, repo_path, repo_push_url):
        pass


@contextlib.contextmanager
def setup_repo_context(repo_url, repo_path, repo_push_url=None):
    """Setup a repository, if an exception is raised then remove the repo.

    :repo_url: string url of the repo to clone
    :repo_path: string path to clone the repo to
    :repo_push_url: string url to push to, or None
    :returns: None

    """
    # if there's any failure after cloning then we should remove the repo
    if repo_push_url is not None:
        phlsys_subprocess.run(
            'git', 'clone', repo_url, repo_path,
            '--config', 'remote.origin.pushurl=' + repo_push_url)
    else:
        phlsys_subprocess.run(
            'git', 'clone', repo_url, repo_path)

    try:
        repo = phlsys_git.Repo(repo_path)

        # make sure we have no problems with 'ident' strings, we won't build
        # from arcyd so it shouldn't be externally visible that we don't expand
        # them.
        phlgitx_ignoreattributes.ensure_repo_ignoring(repo_path)

        # test pushing to master
        repo('checkout', 'origin/master')
        phlgit_commit.allow_empty(repo, 'test commit for pushing')
        repo('push', 'origin', '--dry-run', 'HEAD:refs/heads/master')
        repo('checkout', '-')

        try_push_special_refs(repo)

        # fetch the 'landed' and 'abandoned' refs if they exist
        abdt_git.checkout_master_fetch_special_refs(repo, 'origin')

        ensure_reserve_branch(repo)

        # success, allow the caller to do work
        yield
    except Exception:
        # clean up the git repo on any exception
        shutil.rmtree(repo_path)
        raise


def try_push_special_refs(repo):
    """Try pushing to the special refs that arcyd uses.

    Allow errors to raise through.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: None

    """
    # test pushing to the 'private' dev/arcyd/ area, where arcyd will store
    # it's tracker branches
    repo('push', 'origin', '--dry-run', 'HEAD:refs/heads/dev/arcyd/test')

    # test pushing to the refs/arcyd area, where the 'landed' and 'abandoned'
    # archive branches will live
    repo('push', 'origin', '--dry-run', 'HEAD:refs/arcyd/test')


def is_remote_reserve_branch_present(repo):
    """Return True if the remote for 'repo' is reserving 'dev/arcyd/*'.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: True or False

    """
    reserve_name = phlgitu_ref.Name(_RESERVE_BRANCH_FQ_NAME)
    remote_ref_names = repo("ls-remote").split()[1::2]
    return reserve_name.fq in remote_ref_names


def ensure_reserve_branch(repo):
    """Ensure that the supplied 'repo' remote has the reserve branch.

    To prevent the problem where someone pushes branch 'dev', which blocks
    arcyd's tracker branches from being created.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: None

    """
    reserve_name = phlgitu_ref.Name(_RESERVE_BRANCH_FQ_NAME)
    if not is_remote_reserve_branch_present(repo):
        phlgit_checkout.orphan_clean(repo, reserve_name.short)
        phlgit_commit.allow_empty(repo, _RESERVE_BRANCH_MESSAGE)
        phlgit_push.push(repo, reserve_name.short, 'origin')
        phlgit_checkout.previous_branch(repo)
        phlgit_branch.force_delete(repo, reserve_name.short)


def is_legacy_landinglog_branch_present(repo):
    """Return True if the remote for 'repo' has the legacy landing log ref.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: True or False

    """
    legacy_landinglog_name = phlgitu_ref.Name(_LEGACY_LANDINGLOG_NAME)
    remote_ref_names = repo("ls-remote").split()[1::2]
    return legacy_landinglog_name.fq in remote_ref_names


def remove_landinglog(repo):
    """Remove the legacy landing log ref for the 'origin' of 'repo'.

    Behaviour is undefined if the landing log ref is not present, use
    'is_legacy_landinglog_branch_present' to determine this first.

    :repo: a callable supporting git commands, e.g. repo("status")
    :returns: None

    """
    legacy_landinglog_name = phlgitu_ref.Name(_LEGACY_LANDINGLOG_NAME)
    phlgit_push.delete(repo, 'origin', legacy_landinglog_name.fq)


# -----------------------------------------------------------------------------
# Copyright (C) 2014-2015 Bloomberg Finance L.P.
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
