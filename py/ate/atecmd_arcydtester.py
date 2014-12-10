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
import json
import os
import shutil
import subprocess
import tempfile

import phldef_conduit
import phlgit_push
import phlgitu_fixture
import phlsys_fs
import phlsys_git
import phlsys_subprocess
import phlsys_timer

_USAGE_EXAMPLES = """
"""


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    parser.add_argument(
        '--phab-uri',
        type=str,
        default=phldef_conduit.TEST_URI,
        help='URI of Phabricator instance to connect to, defaults to expect a '
             'phabricator-tools provisioned local install.')

    def make_creds_from_account(account):
        return (
            account.user,
            account.email,
            account.certificate,
        )

    parser.add_argument(
        '--arcyd-user-email-cert',
        type=str,
        nargs=3,
        default=make_creds_from_account(phldef_conduit.PHAB),
        help='The username, email address and conduit certificate of the '
             'arcyd user, default to the "phab" user in a phabricator-tools '
             'provisioned install. The user should be an administrator of the '
             'instance.')

    parser.add_argument(
        '--alice-user-email-cert',
        type=str,
        nargs=3,
        default=make_creds_from_account(phldef_conduit.ALICE),
        help='The username, email address and conduit certificate of the '
             '"alice" user, default to the "alice" user in a '
             'phabricator-tools provisioned install. The user should be an '
             'administrator of the instance.')

    parser.add_argument(
        '--bob-user-email-cert',
        type=str,
        nargs=3,
        default=make_creds_from_account(phldef_conduit.BOB),
        help='The username, email address and conduit certificate of the '
             '"bob" user, default to the "bob" user in a phabricator-tools '
             'provisioned install. The user should be an administrator of the '
             'instance.')

    args = parser.parse_args()

    with phlsys_fs.chtmpdir_context():
        _do_tests(args)


class _Worker(object):

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
        self._barc = _CommandWithWorkingDirectory(barc_cmd_path, working_dir)
        self._arcyon = _CommandWithWorkingDirectory(
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

    def push_new_review_branch(self, identifier):
        branch_name = 'r/master/{}'.format(identifier)
        self._git_worker.commit_new_file_on_new_branch(
            branch=branch_name,
            message='Making review for {}'.format(identifier),
            relative_path=identifier,
            base='origin/master')
        return phlgit_push.push(self._repo, branch_name, 'origin')

    def fetch(self):
        self._repo('fetch', '--prune')

    def list_reviews(self):
        return json.loads(self.barc('list', '--format-json'))

    def accept_review(self, review_id):
        connection_args = [
            '--user', self._phab_username,
            '--cert', self._conduit_cert,
            '--uri', self._phab_uri,
        ]
        self._arcyon(
            'comment',
            review_id,
            '--message', 'accepting',
            '--action', 'accept',
            *connection_args)

    @property
    def repo(self):
        return self._repo

    @property
    def barc(self):
        return self._barc


class _SharedRepo(object):

    def __init__(
            self,
            root_dir,
            barc_cmd_path,
            arcyon_cmd_path,
            phab_uri,
            alice,
            bob):

        self._root_dir = root_dir
        central_path = os.path.join(self._root_dir, 'central')
        os.makedirs(central_path)
        self._central_repo = phlsys_git.Repo(central_path)
        self._central_repo("init", "--bare")

        self._workers = []
        for account in (alice, bob):
            account_user = account[0]
            account_email = account[1]
            account_cert = account[2]
            worker_path = os.path.join(self._root_dir, account_user)
            os.makedirs(worker_path)
            self._workers.append(
                _Worker(
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


class _CommandWithWorkingDirectory(object):

    def __init__(self, command_path, working_dir_path):
        self._working_dir_path = os.path.abspath(working_dir_path)
        self._command_path = os.path.abspath(command_path)

    def __call__(self, *args, **kwargs):
        stdin = kwargs.pop("stdin", None)
        assert(not kwargs)
        result = phlsys_subprocess.run(
            self._command_path, *args,
            stdin=stdin, workingDir=self._working_dir_path)
        return result.stdout


class _ArcydInstance(object):

    def __init__(self, root_dir, arcyd_command):
        self._root_dir = root_dir
        self._command = _CommandWithWorkingDirectory(arcyd_command, root_dir)

    def __call__(self, *args, **kwargs):
        return self._command(*args, **kwargs)

    def run_once(self):
        return self('start', '--foreground', '--no-loop')

    def debug_log(self):
        return phlsys_fs.read_text_file(
            '{}/var/log/debug'.format(self._root_dir))


class _Fixture(object):

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
                _SharedRepo(
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
            self._arcyds.append(_ArcydInstance(arcyd_path, arcyd_command))

    def close(self):
        shutil.rmtree(self._root_dir)

    def launch_debug_shell(self):
        with phlsys_fs.chdir_context(self._root_dir):
            print "Launching debug shell, exit the shell to continue ..."
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


def _do_tests(args):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    py_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(py_dir)
    arcyd_cmd_path = os.path.join(root_dir, 'proto', 'arcyd')
    barc_cmd_path = os.path.join(root_dir, 'proto', 'barc')
    arcyon_cmd_path = os.path.join(root_dir, 'bin', 'arcyon')
    phab_uri = args.phab_uri
    arcyd_user, arcyd_email, arcyd_cert = args.arcyd_user_email_cert

    # pychecker makes us declare this before 'with'
    repo_count = 10
    arcyd_count = 1
    with phlsys_timer.print_duration_context("Fixture setup"):
        fixture = _Fixture(
            arcyd_cmd_path,
            barc_cmd_path,
            arcyon_cmd_path,
            phab_uri,
            repo_count,
            arcyd_count,
            args.alice_user_email_cert,
            args.bob_user_email_cert)
    with contextlib.closing(fixture):
        with phlsys_timer.print_duration_context("Arcyd setup"):
            arcyd = fixture.arcyds[0]

            arcyd('init', '--arcyd-email', arcyd_email)

            arcyd(
                'add-phabricator',
                '--name', 'localphab',
                '--instance-uri', phab_uri,
                '--review-url-format', phldef_conduit.REVIEW_URL_FORMAT,
                '--admin-emails', 'local-phab-admin@localhost',
                '--arcyd-user', arcyd_user,
                '--arcyd-cert', arcyd_cert)

            repo_url_format = '{}/{{}}/central'.format(fixture.repo_root_dir)
            arcyd(
                'add-repohost',
                '--name', 'localdir',
                '--repo-url-format', repo_url_format)

        with phlsys_timer.print_duration_context("Add repos to arcyd"):
            for i in xrange(repo_count):
                arcyd('add-repo', 'localphab', 'localdir', 'repo-{}'.format(i))

        with phlsys_timer.print_duration_context("Pushing reviews"):
            for i in xrange(repo_count):
                worker = fixture.repos[i].alice
                worker.push_new_review_branch('review1')

        with phlsys_timer.print_duration_context("Creating reviews"):
            arcyd.run_once()

        with phlsys_timer.print_duration_context("Accepting reviews"):
            for i in xrange(repo_count):
                bob = fixture.repos[i].bob
                bob.fetch()
                reviews = bob.list_reviews()
                assert len(reviews) == 1
                r = reviews[0]
                bob.accept_review(r["review_id"])

        with phlsys_timer.print_duration_context("Landing reviews"):
            arcyd.run_once()

        with phlsys_timer.print_duration_context("Update nothing"):
            arcyd.run_once()


        # launch a debug shell for the user to poke around in
        # fixture.launch_debug_shell()


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
