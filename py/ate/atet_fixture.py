"""Creates a fixture with Arcyd setup to perform tests."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# atet_fixture
#
# Public Classes:
#   Fixture
#    .setup_arcyds
#    .close
#    .launch_debug_shell
#    .repos
#    .arcyds
#    .repo_root_dir
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import shutil
import subprocess
import tempfile

import phldef_conduit
import phlsys_fs

import atet_arcyd_instance
import atet_sharedrepo


class Fixture(object):

    def __init__(
            self,
            arcyd_command,
            barc_command,
            arcyon_command,
            phab_uri,
            repo_count,
            arcyd_count,
            alice,
            bob):
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
            self._repos.append(
                atet_sharedrepo.SharedRepo(
                    repo_path,
                    barc_command,
                    arcyon_command,
                    phab_uri,
                    alice,
                    bob))

        self._arcyd_root_dir = os.path.join(self._root_dir, 'arcyds')
        os.makedirs(self._arcyd_root_dir)
        self._arcyds = []
        for i in xrange(arcyd_count):
            arcyd_path = os.path.join(
                self._arcyd_root_dir, 'arcyd-{}'.format(i))
            os.makedirs(arcyd_path)
            self._arcyds.append(atet_arcyd_instance.ArcydInstance(
                arcyd_path, arcyd_command))

    def setup_arcyds(self, arcyd_user, arcyd_email, arcyd_cert, phab_uri):
        for arcyd in self.arcyds:
            arcyd(
                'init',
                '--arcyd-email',
                arcyd_email,
                '--max-workers',
                '2',
                '--sleep-secs',
                '1')

            arcyd(
                'add-phabricator',
                '--name', 'localphab',
                '--instance-uri', phab_uri,
                '--review-url-format', phldef_conduit.REVIEW_URL_FORMAT,
                '--admin-emails', 'local-phab-admin@localhost',
                '--arcyd-user', arcyd_user,
                '--arcyd-cert', arcyd_cert)

            repo_url_format = '{}/{{}}/central'.format(self.repo_root_dir)
            arcyd(
                'add-repohost',
                '--name', 'localdir',
                '--repo-url-format', repo_url_format)

    def close(self):
        for r in self._repos:
            r.close()
        shutil.rmtree(self._root_dir)

    def launch_debug_shell(self):
        with phlsys_fs.chdir_context(self._root_dir):
            print("Launching debug shell, exit the shell to continue ...")
            subprocess.call('bash')

    @property
    def repos(self):
        return self._repos

    @property
    def arcyds(self):
        return self._arcyds

    @property
    def repo_root_dir(self):
        return self._repo_root_dir


# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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
