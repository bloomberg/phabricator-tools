"""Arcyd - daemon to watch git repos, create and land reviews automatically.

Intended to make it easy for large teams to start using Differential without
individual contributors needing to install and configure Arcanist.

Individual contributors are still free to use Arcanist if they wish, Arcyd
provides a zero-config layer over Git to get them started.

Arcyd does the following:
- watches for specially named branches and automatically creates revisions
- automatically updates revisions when the branch changes
- automatically lands revisions when they are approved

minimal user workflow:
    $ git checkout feature/mywork
    ~ commit some work on the branch ~
    $ git push origin feature/mywork:arcyd-review/mywork/master

    .. Arcyd see's the 'arcyd-review' branch and creates a review ..
    .. Reviewer accepts the change ..
    .. Arcyd squashes the 'arcyd-review' branch onto master and deletes it ..

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_arcyd
#
# Public Functions:
#   main
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import argparse

import phlsys_subcommand

import abdcmd_addphabricator
import abdcmd_addrepo
import abdcmd_addrepohost
import abdcmd_arcydstatushtml
import abdcmd_fetch
import abdcmd_fsck
import abdcmd_init
import abdcmd_listrepos
import abdcmd_repostatushtml
import abdcmd_rmrepo
import abdcmd_start
import abdcmd_stop

_USAGE_EXAMPLES = """
usage example:
To setup arcyd using the example accounts baked into the 'phabricator-tools'
vagrant/puppet installation. (see ./README)

    $ mkdir arcyd
    $ cd arcyd
    $ arcyd init --arcyd-email arcyd@localhost
    $ arcyd add-phabricator \\
        --name local \\
        --instance-uri http://127.0.0.1/api/ \\
        --review-url-format 'http://127.0.0.1/D{review}' \\
        --admin-emails 'local-phab-admin@localhost' \\
        --arcyd-user phab \\
        --arcyd-cert \\
xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrvafgzqu\
zl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w6lcseh\
s2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk3lyr3u\
vot7fxrotwpi3ty2b2sa2kvlpf

    $ arcyd add-repohost \\
        --name local_repos \\
        --repo-url-format '/path/to/repos/{}'

    $ arcyd add-repo \\
        --name local_1 \\
        --repo-url local_1 \\
        --repo-desc local_1 \\
        --phabricator-name local \\
        --repohost-name local_repos \\
        --admin-emails 'local-repo1-admin@localhost'

    $ arcyd start

run each command with the '--help' option for more information, e.g.:

    $ arcyd init --help

    """


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    subparsers = parser.add_subparsers()

    phlsys_subcommand.setup_parser(
        "arcyd-status-html", abdcmd_arcydstatushtml, subparsers)
    phlsys_subcommand.setup_parser(
        "repo-status-html", abdcmd_repostatushtml, subparsers)
    phlsys_subcommand.setup_parser(
        "init", abdcmd_init, subparsers)
    phlsys_subcommand.setup_parser(
        "list-repos", abdcmd_listrepos, subparsers)
    phlsys_subcommand.setup_parser(
        "add-phabricator", abdcmd_addphabricator, subparsers)
    phlsys_subcommand.setup_parser(
        "add-repohost", abdcmd_addrepohost, subparsers)
    phlsys_subcommand.setup_parser(
        "add-repo", abdcmd_addrepo, subparsers)
    phlsys_subcommand.setup_parser(
        "rm-repo", abdcmd_rmrepo, subparsers)
    phlsys_subcommand.setup_parser(
        "start", abdcmd_start, subparsers)
    phlsys_subcommand.setup_parser(
        "stop", abdcmd_stop, subparsers)
    phlsys_subcommand.setup_parser(
        "fsck", abdcmd_fsck, subparsers)
    phlsys_subcommand.setup_parser(
        "fetch", abdcmd_fetch, subparsers)

    args = parser.parse_args()

    return args.func(args)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
