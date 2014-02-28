"""Add a new repository for the Arcyd instance to manage."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_addrepo
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import argparse
import os
import shutil

import phlgit_commit
import phlsys_git
import phlsys_subprocess
import phlurl_request

import abdi_repoargs
import abdt_fs
import abdt_git


_CONFIG = """
@{phabricator_config}
@{repohost_config}
--repo-desc
{repo_desc}
--repo-url
{repo_url}
--repo-path
{repo_path}
--try-touch-path
{try_touch_path}
--ok-touch-path
{ok_touch_path}
""".strip()

_CONFIG_ADMIN_EMAILS_FORMAT = """
--admin-emails
{admin_emails}
""".strip()


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--name',
        type=str,
        metavar='STR',
        required=True,
        help="string identifier for the repository, '[_a-zA-Z0-9]+'.")

    parser.add_argument(
        '--phabricator-name',
        type=str,
        metavar='STR',
        required=True,
        help="name of the Phabricator instance associated with the repo.")

    parser.add_argument(
        '--repohost-name',
        type=str,
        metavar='STR',
        required=True,
        help="name of the repohost associated with the repo.")

    parser.add_argument(
        '--repo-desc',
        type=str,
        metavar='STR',
        required=True,
        help="very short description of the repository, appears on the "
             "dashboard, in error messages and in logs.")

    parser.add_argument(
        '--repo-url',
        metavar="URL",
        type=str,
        required=True,
        help="url to clone the repository, e.g. 'github:org/repo' or maybe "
             "something like 'org/repo' if using '--repo-url-format'.")

    parser.add_argument(
        '--admin-emails',
        nargs='*',
        metavar="TO",
        type=str,
        help="list of email addresses to send important repo events to")


def process(args):

    fs = abdt_fs.make_default_accessor()

    try_touch_path = fs.layout.repo_try(args.name)
    ok_touch_path = fs.layout.repo_ok(args.name)
    repo_path = fs.layout.repo(args.name)

    # make sure the repo doesn't exist already
    if os.path.exists(repo_path):
        raise Exception('{} already exists'.format(repo_path))

    # make sure the phabricator config exists
    phab_config_path = fs.get_phabricator_config_rel_path(
        args.phabricator_name)

    # make sure the repohost config exists
    repohost_config_path = fs.get_repohost_config_rel_path(
        args.repohost_name)

    # generate the config file
    config = _CONFIG.format(
        phabricator_config=phab_config_path,
        repohost_config=repohost_config_path,
        repo_desc=args.repo_desc,
        repo_url=args.repo_url,
        repo_path=repo_path,
        try_touch_path=try_touch_path,
        ok_touch_path=ok_touch_path)

    if args.admin_emails:
        config = '\n'.join([
            config,
            _CONFIG_ADMIN_EMAILS_FORMAT.format(
                admin_emails='\n'.join(args.admin_emails))])

    # parse the arguments again, as a real repo
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    abdi_repoargs.setup_parser(parser)
    repo_args = config.splitlines()
    repo_params = parser.parse_args(repo_args)

    abdi_repoargs.validate_args(repo_params)

    # make sure we can use the snoop URL
    repo_snoop_url = abdi_repoargs.get_repo_snoop_url(repo_params)
    if repo_snoop_url:
        phlurl_request.get(repo_snoop_url)

    # determine the repo url from the parsed params
    repo_url = abdi_repoargs.get_repo_url(repo_params)

    # if there's any failure after cloning then we should remove the repo
    phlsys_subprocess.run(
        'git', 'clone', repo_url, repo_path)
    try:
        repo = phlsys_git.Repo(repo_path)

        # test pushing to master
        repo.call('checkout', 'origin/master')
        phlgit_commit.allow_empty(repo, 'test commit for pushing')
        repo.call('push', 'origin', '--dry-run', 'HEAD:refs/heads/master')
        repo.call('checkout', '-')

        # test push to special refs
        repo.call(
            'push', 'origin', '--dry-run', 'HEAD:refs/arcyd/test')
        repo.call(
            'push', 'origin', '--dry-run', 'HEAD:refs/heads/dev/arcyd/test')

        # fetch the 'landed' and 'abandoned' refs if they exist
        ref_list = set(repo.call('ls-remote').split()[1::2])
        special_refs = [
            (abdt_git.ARCYD_ABANDONED_REF, abdt_git.ARCYD_ABANDONED_BRANCH_FQ),
            (abdt_git.ARCYD_LANDED_REF, abdt_git.ARCYD_LANDED_BRANCH_FQ),
        ]
        for ref in special_refs:
            if ref[0] in ref_list:
                repo.call('fetch', 'origin', '{}:{}'.format(ref[0], ref[1]))

        # success, write out the config
        fs.create_repo_config(args.name, config)
    except Exception:
        # clean up the git repo
        shutil.rmtree(repo_path)
        raise


#------------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
