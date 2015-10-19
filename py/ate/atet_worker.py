"""Utilities to simulate a person working with Phabricator, Git and Arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# atet_worker
#
# Public Classes:
#   Worker
#    .setup
#    .push_initial_commit
#    .push_new_review_branch
#    .push_review_update
#    .fetch
#    .list_reviews
#    .accept_review
#    .request_changes
#    .repo
#    .barc
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

import phlgit_push
import phlgitu_fixture
import phlsys_workingdircommand


class Worker(object):
    """Simulate a person working with Phabricator, Git and Arcyd."""

    def __init__(
            self,
            repo,
            working_dir,
            barc_cmd_path,
            phab_username,
            email,
            conduit_cert,
            arcyon_cmd_path,
            phab_uri):
        self._repo = repo
        self._barc = phlsys_workingdircommand.CommandWithWorkingDirectory(
            barc_cmd_path, working_dir)
        self._arcyon = phlsys_workingdircommand.CommandWithWorkingDirectory(
            arcyon_cmd_path, working_dir)
        self._working_dir = working_dir
        self._git_worker = phlgitu_fixture.Worker(repo)
        self._phab_username = phab_username
        self._email = email
        self._conduit_cert = conduit_cert
        self._phab_uri = phab_uri

    def setup(self, central_repo_path):
        self._repo("init")
        self._repo('config', 'user.name', self._phab_username)
        self._repo('config', 'user.email', self._email)
        self._repo("remote", "add", "origin", central_repo_path)
        self._repo("fetch")

    def push_initial_commit(self):
        self._git_worker.commit_new_file('initial commit', 'README')
        phlgit_push.push(self._repo, 'master', 'origin')

    def push_new_review_branch(self, identifier, message=None):
        branch_name = 'r/master/{}'.format(identifier)

        if message is None:
            message = 'Making review for {}'.format(identifier)

        self._git_worker.commit_new_file_on_new_branch(
            branch=branch_name,
            message=message,
            relative_path=identifier,
            base='origin/master')
        return phlgit_push.push(self._repo, branch_name, 'origin')

    def push_review_update(self, identifier, to_append):
        self._git_worker.commit_append_to_file(
            identifier, identifier, to_append)

        branch_name = 'r/master/{}'.format(identifier)
        phlgit_push.push(self._repo, branch_name, 'origin')

    def fetch(self):
        self._repo('fetch', '--prune')

    def list_reviews(self):
        return json.loads(self._barc('list', '--format-json'))

    def _arcyon_action(self, review_id, action):
        connection_args = [
            '--user', self._phab_username,
            '--cert', self._conduit_cert,
            '--uri', self._phab_uri,
        ]
        self._arcyon(
            'comment',
            review_id,
            '--message', 'accepting',
            '--action', action,
            *connection_args)

    def accept_review(self, review_id):
        self._arcyon_action(review_id, 'accept')

    def request_changes(self, review_id):
        self._arcyon_action(review_id, 'request changes')

    @property
    def repo(self):
        return self._repo

    @property
    def barc(self):
        return self._barc


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
