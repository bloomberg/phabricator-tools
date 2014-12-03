"""Arcyd tester - command-line utility to exercise arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# atecmd_arcydtester
#
# Public Functions:
#   main
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import argparse
import contextlib
import os
import shutil
import tempfile

import phlgit_push
import phlgitu_fixture
import phlsys_fs
import phlsys_git

_USAGE_EXAMPLES = """
"""


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    parser.parse_args()

    with phlsys_fs.chtmpdir_context():
        _do_tests()


class _SharedRepo(object):

    def __init__(self, root_dir=None, worker_count=1):
        if worker_count < 1:
            raise(
                Exception("worker_count must be 1 or more, got {}".format(
                    worker_count)))

        self._root_dir = root_dir
        central_path = os.path.join(self._root_dir, 'central')
        os.makedirs(central_path)
        self._central_repo = phlsys_git.Repo(central_path)
        self._central_repo("init", "--bare")

        self._workers = []
        for i in xrange(worker_count):
            worker_path = os.path.join(self._root_dir, 'worker-{}'.format(i))
            os.makedirs(worker_path)
            self._workers.append(
                phlgitu_fixture.Worker(phlsys_git.Repo(worker_path)))
            self._workers[-1].repo("init")
            self._workers[-1].repo(
                "remote", "add", "origin", self._central_repo.working_dir)
            self._workers[-1].repo("fetch")

            if i == 0:
                self._workers[0].commit_new_file('initial commit', 'README')
                phlgit_push.push(self._workers[0].repo, 'master', 'origin')
            else:
                self._workers[i].repo('fetch')
                self._workers[i].repo('checkout', 'master')

    @property
    def central_repo(self):
        return self._central_repo

    @property
    def workers(self):
        return self._workers


class _Fixture(object):

    def __init__(self, repo_count=1, arcyd_count=1):
        if repo_count < 1:
            raise(Exception("repo_count must be 1 or more, got {}".format(
                repo_count)))
        if arcyd_count < 1:
            raise(Exception("arcyd_count must be 1 or more, got {}".format(
                arcyd_count)))

        self._root_dir = tempfile.mkdtemp()
        self._repo_root_dir = os.path.join(self._root_dir, 'repos')
        os.makedirs(self._repo_root_dir)
        self._repos = []
        for i in xrange(repo_count):
            repo_path = os.path.join(self._repo_root_dir, 'repo-{}'.format(i))
            os.makedirs(repo_path)
            self._repos.append(_SharedRepo(repo_path))

    def close(self):
        shutil.rmtree(self._root_dir)

    @property
    def repos(self):
        return self._repos


def _do_tests():
    fixture = _Fixture()  # pychecker makes us declare this before 'with'
    with contextlib.closing(fixture):
        print fixture.repos[0].workers[0].repo('status')


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
