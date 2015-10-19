"""Arcyd tester - command-line utility to exercise arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# atecmd_arcydtester
#
# Public Functions:
#   main
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
import os

import phldef_conduit
import phlsys_fs

import atet_fixture

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
    fixture = atet_fixture.Fixture(
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
    fixture = atet_fixture.Fixture(
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
