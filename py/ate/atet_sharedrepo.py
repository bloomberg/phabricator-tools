"""Simulates a central repository where multiple workers can collaborate."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# atet_sharedrepo
#
# Public Classes:
#   SharedRepo
#    .hold_dev_arcyd_refs
#    .release_dev_arcyd_refs
#    .snoop_url
#    .central_repo
#    .workers
#    .alice
#    .bob
#    .close
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import shutil
import stat

import phlsys_fs
import phlsys_git
import phlsys_web

import atet_worker

_PRE_RECEIVE_HOLD_DEV_ARCYD_REFS = """
#! /bin/sh
if grep 'refs/heads/dev/arcyd/' -; then
    while [ -f command/hold_dev_arcyd_refs ]; do
        sleep 1
    done
fi
""".lstrip()


class SharedRepo(object):

    def __init__(
            self,
            root_dir,
            barc_cmd_path,
            arcyon_cmd_path,
            phab_uri,
            alice,
            bob):

        self._root_dir = root_dir
        self.central_path = os.path.join(self._root_dir, 'central')
        os.makedirs(self.central_path)
        self._central_repo = phlsys_git.Repo(self.central_path)
        self._central_repo("init", "--bare")
        self.web_port = phlsys_web.pick_free_port()
        shutil.move(
            os.path.join(self.central_path, 'hooks/post-update.sample'),
            os.path.join(self.central_path, 'hooks/post-update'))

        self._command_hold_path = os.path.join(
            self.central_path, 'command/hold_dev_arcyd_refs')

        pre_receive_path = os.path.join(self.central_path, 'hooks/pre-receive')
        phlsys_fs.write_text_file(
            pre_receive_path,
            _PRE_RECEIVE_HOLD_DEV_ARCYD_REFS)
        mode = os.stat(pre_receive_path).st_mode
        os.chmod(pre_receive_path, mode | stat.S_IEXEC)

        self._web = phlsys_web.SimpleWebServer(
            self.central_path,
            self.web_port)

        self._workers = []
        for account in (alice, bob):
            account_user = account[0]
            account_email = account[1]
            account_cert = account[2]
            worker_path = os.path.join(self._root_dir, account_user)
            os.makedirs(worker_path)
            self._workers.append(
                atet_worker.Worker(
                    phlsys_git.Repo(worker_path),
                    worker_path,
                    barc_cmd_path,
                    account_user,
                    account_email,
                    account_cert,
                    arcyon_cmd_path,
                    phab_uri))
            self._workers[-1].setup(self._central_repo.working_dir)

            if len(self._workers) == 1:
                self._workers[0].push_initial_commit()
            else:
                self._workers[-1].repo('checkout', 'master')

    def hold_dev_arcyd_refs(self):
        phlsys_fs.write_text_file(
            self._command_hold_path,
            _PRE_RECEIVE_HOLD_DEV_ARCYD_REFS)

    def release_dev_arcyd_refs(self):
        os.remove(self._command_hold_path)

    @property
    def snoop_url(self):
        return "http://127.0.0.1:{}/info/refs".format(self.web_port)

    @property
    def central_repo(self):
        return self._central_repo

    @property
    def workers(self):
        return self._workers

    @property
    def alice(self):
        return self._workers[0]

    @property
    def bob(self):
        return self._workers[1]

    def close(self):
        self._web.close()


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
