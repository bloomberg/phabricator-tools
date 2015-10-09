"""Arcyd tester - command-line utility to exercise arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# atecmd_arcydtester
#
# Public Classes:
#   SimpleWebServer
#    .close
#
# Public Functions:
#   main
#   pick_free_port
#   run_all_interactions
#   run_interaction
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import contextlib
import itertools
import json
import os
import shutil
import socket
import stat
import subprocess
import tempfile
import time

import phldef_conduit
import phlgit_push
import phlgitu_fixture
import phlsys_fs
import phlsys_git
import phlsys_pid
import phlsys_subprocess

_USAGE_EXAMPLES = """
"""

_PRE_RECEIVE_HOLD_DEV_ARCYD_REFS = """
#! /bin/sh
if grep 'refs/heads/dev/arcyd/' -; then
    while [ -f command/hold_dev_arcyd_refs ]; do
        sleep 1
    done
fi
""".lstrip()

_EXTERNAL_REPORT_COUNTER = """
#! /bin/sh
if [ ! -f cycle_counter ]; then
    echo 0 > cycle_counter
    fi

COUNT=$(cat cycle_counter)
COUNT=$(expr $COUNT + 1)

echo $COUNT > cycle_counter
""".lstrip()


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

    parser.add_argument(
        '--repo-count',
        type=int,
        default=1,
        help='The number of repositories to simulate working on, a simple way '
             'to exercise concurrency and gather more accurate performance '
             'information.')

    parser.add_argument(
        '--enable-debug-shell',
        action='store_true',
        default=False,
        help='If this argument is provided, debug shell is launched '
             'automatically if any of the tests fail. By default, this option '
             'is set to false.')

    args = parser.parse_args()

    with phlsys_fs.chtmpdir_context():
        _do_tests(args)


def pick_free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


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


class SimpleWebServer(object):

    def __init__(self, root_path, port):
        self._root_path = root_path
        self._process = subprocess.Popen(
            ['python', '-m', 'SimpleHTTPServer', str(port)],
            cwd=root_path)

    def close(self):
        pid = self._process.pid
        phlsys_pid.request_terminate(pid)
        self._process.wait()


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
        self.central_path = os.path.join(self._root_dir, 'central')
        os.makedirs(self.central_path)
        self._central_repo = phlsys_git.Repo(self.central_path)
        self._central_repo("init", "--bare")
        self.web_port = pick_free_port()
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

        self._web = SimpleWebServer(
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

        count_cycles_script_path = os.path.join(
            self._root_dir, 'count_cycles.sh')
        phlsys_fs.write_text_file(
            count_cycles_script_path,
            _EXTERNAL_REPORT_COUNTER)
        mode = os.stat(count_cycles_script_path).st_mode
        os.chmod(count_cycles_script_path, mode | stat.S_IEXEC)

        self._has_enabled_count_cycles = False
        self._has_started_daemon = False
        self._has_set_overrun_secs = False

    def __call__(self, *args, **kwargs):
        return self._command(*args, **kwargs)

    def set_overrun_secs(self, overrun_secs):
        assert not self._has_set_overrun_secs
        config_path = os.path.join(self._root_dir, 'configfile')
        config_text = phlsys_fs.read_text_file(config_path)
        config_text += '\n--overrun-secs\n{}'.format(overrun_secs)
        phlsys_fs.write_text_file(config_path, config_text)
        self._has_set_overrun_secs = True

    def enable_count_cycles_script(self):
        assert not self._has_enabled_count_cycles
        config_path = os.path.join(self._root_dir, 'configfile')
        config_text = phlsys_fs.read_text_file(config_path)
        config_text += '\n--external-report-command\ncount_cycles.sh'
        phlsys_fs.write_text_file(config_path, config_text)
        self._has_enabled_count_cycles = True

    def count_cycles(self):
        assert self._has_enabled_count_cycles
        counter_path = os.path.join(self._root_dir, 'cycle_counter')
        if not os.path.exists(counter_path):
            return None
        return int(phlsys_fs.read_text_file(counter_path).strip())

    def wait_one_or_more_cycles(self):
        assert self._has_enabled_count_cycles
        assert self._has_started_daemon
        while self.count_cycles() is None:
            time.sleep(1)
        start = self.count_cycles()
        count = start
        while count < start + 2:
            count = self.count_cycles()
            print(start, count)
            time.sleep(1)

    def run_once(self):
        return self('start', '--foreground', '--no-loop')

    def start_daemon(self):
        self._has_started_daemon = True
        return self('start')

    def stop_daemon(self):
        self._has_started_daemon = False
        return self('stop')

    @contextlib.contextmanager
    def daemon_context(self):
        self.start_daemon()
        try:
            yield
        finally:
            self.stop_daemon()

    def _read_log(self, name):
        log_path = '{}/var/log/{}'.format(self._root_dir, name)

        if os.path.isfile(log_path):
            return phlsys_fs.read_text_file(
                log_path)
        else:
            return ""

    def info_log(self):
        return self._read_log('info')

    def debug_log(self):
        return self._read_log('debug')


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


def _do_tests(args):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    py_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(py_dir)
    arcyd_cmd_path = os.path.join(
        root_dir, 'testbed', 'arcyd-tester', 'git_fetch_counter_arcyd.py')
    barc_cmd_path = os.path.join(root_dir, 'proto', 'barc')
    arcyon_cmd_path = os.path.join(root_dir, 'bin', 'arcyon')
    phab_uri = args.phab_uri
    arcyd_user, arcyd_email, arcyd_cert = args.arcyd_user_email_cert

    # pychecker makes us declare this before 'with'
    arcyd_count = 1
    fixture = _Fixture(
        arcyd_cmd_path,
        barc_cmd_path,
        arcyon_cmd_path,
        phab_uri,
        args.repo_count,
        arcyd_count,
        args.alice_user_email_cert,
        args.bob_user_email_cert)
    fixture.setup_arcyds(arcyd_user, arcyd_email, arcyd_cert, phab_uri)
    with contextlib.closing(fixture):
        try:
            run_all_interactions(fixture)
        except Exception:
            print(fixture.arcyds[0].debug_log())
            if args.enable_debug_shell:
                fixture.launch_debug_shell()
            raise

    repo_count = 4
    fixture = _Fixture(
        arcyd_cmd_path,
        barc_cmd_path,
        arcyon_cmd_path,
        phab_uri,
        repo_count,
        arcyd_count,
        args.alice_user_email_cert,
        args.bob_user_email_cert)
    fixture.setup_arcyds(arcyd_user, arcyd_email, arcyd_cert, phab_uri)

    with contextlib.closing(fixture):
        try:
            _test_push_during_overrun(fixture)
        except Exception:
            print(fixture.arcyds[0].debug_log())
            if args.enable_debug_shell:
                fixture.launch_debug_shell()
            raise


def run_all_interactions(fixture):
    arcyd = fixture.arcyds[0]
    arcyd_generator = _arcyd_run_once_scenario(arcyd, fixture.repos)

    interaction_tuple = (
        _user_story_happy_path,
        _user_story_request_changes,
        _user_story_reviewers_as_title,
    )

    for interaction in interaction_tuple:
        run_interaction(
            interaction,
            arcyd_generator,
            fixture)


def _test_push_during_overrun(fixture):
    arcyd = fixture.arcyds[0]
    repo = fixture.repos[0]
    phab_str = 'localphab'
    repohost_prefix = 'repohost'
    repo_prefix = 'repo'

    for i, r in enumerate(fixture.repos):
        repo_url_format = r.central_path
        arcyd(
            'add-repohost',
            '--name', 'repohost-{}'.format(i),
            '--repo-url-format', repo_url_format,
            '--repo-snoop-url-format', r.snoop_url)
        arcyd(
            'add-repo',
            phab_str,
            '{}-{}'.format(repohost_prefix, i),
            '{}-{}'.format(repo_prefix, i))

    branch1_name = '_test_push_during_overrun'
    branch2_name = '_test_push_during_overrun2'

    arcyd.enable_count_cycles_script()
    arcyd.set_overrun_secs(1)
    repo.hold_dev_arcyd_refs()
    repo.alice.push_new_review_branch(branch1_name)
    with arcyd.daemon_context():
        arcyd.wait_one_or_more_cycles()
        repo.alice.push_new_review_branch(branch2_name)
        arcyd.wait_one_or_more_cycles()
        repo.release_dev_arcyd_refs()
        arcyd.wait_one_or_more_cycles()
        arcyd.wait_one_or_more_cycles()

    repo.alice.fetch()
    reviews = repo.alice.list_reviews()
    assert len(reviews) == 2

    fetch_counter_path = os.path.join(
        arcyd._root_dir,
        'var',
        'repo',
        '{}_{}-0_{}-0'.format(phab_str, repohost_prefix, repo_prefix),
        '.git',
        'fetch_counter')
    fetch_count = int(phlsys_fs.read_text_file(fetch_counter_path))
    assert fetch_count == 4


def run_interaction(user_scenario, arcyd_generator, fixture):
    user_scenario_list = [user_scenario(repo) for repo in fixture.repos]
    for interactions in itertools.izip(*user_scenario_list):
        print(interactions)
        next(arcyd_generator)


def _arcyd_run_once_scenario(arcyd, repo_list):

    # Add repositories to the single Arcyd instance
    for i in xrange(len(repo_list)):
        arcyd('add-repo', 'localphab', 'localdir', 'repo-{}'.format(i))

    while True:
        arcyd.run_once()
        yield


def _user_story_happy_path(repo):

    branch_name = '_user_story_happy_path'

    print("Push review")
    repo.alice.push_new_review_branch(branch_name)

    yield "Creating reviews"

    print("Accept review")
    repo.bob.fetch()
    reviews = repo.bob.list_reviews()
    assert len(reviews) == 1
    repo.bob.accept_review(reviews[0]["review_id"])

    yield "Landing reviews"

    print("Check review landed")
    repo.bob.fetch()
    assert len(repo.bob.list_reviews()) == 0

    yield "Finished"


def _user_story_request_changes(repo):

    branch_name = '_user_story_request_changes'

    print("Push review")
    repo.alice.push_new_review_branch(branch_name)

    yield "Creating reviews"
    repo.bob.fetch()
    review_id = repo.bob.list_reviews()[0]["review_id"]

    print("Request changes")
    repo.bob.request_changes(review_id)
    yield "Nothing"

    yield "Update review"
    repo.alice.push_review_update(branch_name, 'more changes')

    print("Accept review")
    repo.bob.accept_review(review_id)

    yield "Landing reviews"

    print("Check review landed")
    repo.bob.fetch()
    assert len(repo.bob.list_reviews()) == 0

    yield "Finished"


def _user_story_reviewers_as_title(repo):

    branch_name = '_user_story_reviewers_as_title'

    message = """Reviewers: alice

    Here is the real title.
    """

    repo.alice.push_new_review_branch(
        branch_name, message=message)

    yield "Creating reviews"

    print("Accept review")
    repo.bob.fetch()
    reviews = repo.bob.list_reviews()
    assert len(reviews) == 1
    repo.bob.accept_review(reviews[0]["review_id"])

    yield "Landing reviews"

    print("Check review landed")
    repo.bob.fetch()
    assert len(repo.bob.list_reviews()) == 0

    yield "Finished"


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
