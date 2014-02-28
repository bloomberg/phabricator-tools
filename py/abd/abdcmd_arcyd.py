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
import abdcmd_arcydstatushtml
import abdcmd_devstatushtml
import abdcmd_init
import abdcmd_instaweb
import abdcmd_repostatushtml
import abdcmd_start
import abdcmd_stop

_USAGE_EXAMPLES = """
usage example:
    Using the example accounts baked into the 'phabricator-tools'
    vagrant/puppet installation. (see ./README)

    You can also split the configuration across multiple files and combine them
    on the command-line or have them inherit from eachother.

    ** TODO: test this config **

    in localinstance.cfg:
        --instance-uri
        https://127.0.0.1/api/
        --arcyd-user
        phab
        --arcyd-cert
        xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7\
ru3lrvafgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo\
2j3y2w6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5\
rpicdk3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

    in email.cfg:
        --arcyd-email
        phab-role-account@server.example
        --admin-email
        admin@server.example

    in repo1.cfg:
        @localinstance.cfg
        @email.cfg
        --repo-desc
        http://server.example/repo.git
        --repo-path
        /path/to/repo

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
        "dev-status-html", abdcmd_devstatushtml, subparsers)
    phlsys_subcommand.setup_parser(
        "instaweb", abdcmd_instaweb, subparsers)
    phlsys_subcommand.setup_parser(
        "init", abdcmd_init, subparsers)
    phlsys_subcommand.setup_parser(
        "add-phabricator", abdcmd_addphabricator, subparsers)
    phlsys_subcommand.setup_parser(
        "add-repo", abdcmd_addrepo, subparsers)
    phlsys_subcommand.setup_parser(
        "start", abdcmd_start, subparsers)
    phlsys_subcommand.setup_parser(
        "stop", abdcmd_stop, subparsers)

    args = parser.parse_args()

    args.func(args)


#------------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
#------------------------------- END-OF-FILE ----------------------------------
