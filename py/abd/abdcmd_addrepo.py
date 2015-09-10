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
from __future__ import division
from __future__ import print_function

import argparse
import os

import phlurl_request

import abdi_repo
import abdi_repoargs
import abdt_fs


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
        'phabricator_name',
        type=str,
        help="name of the Phabricator instance associated with the repo.")

    parser.add_argument(
        'repohost_name',
        type=str,
        help="name of the repohost associated with the repo.")

    parser.add_argument(
        'repo_url',
        type=str,
        help="url to clone the repository, e.g. 'github:org/repo' or maybe "
             "something like 'org/repo' if using '--repo-url-format'.")

    parser.add_argument(
        '--name',
        type=str,
        metavar='STR',
        help="string identifier for the repository, '{regex}'. "
             "will guess a name from the mandatory args if "
             "none provided.".format(regex=abdt_fs.CONFIG_NAME_REGEX))

    parser.add_argument(
        '--repo-desc',
        type=str,
        metavar='STR',
        help="very short description of the repository, appears on the "
             "dashboard, in error messages and in logs. "
             "will guess a name from the mandatory args if none provided.")

    parser.add_argument(
        '--admin-emails',
        nargs='*',
        metavar="TO",
        type=str,
        help="list of email addresses to send important repo events to")


def _repo_desc_for_params(phab, repohost, url):
    return "{url}".format(
        phab=phab, repohost=repohost, url=url)


def _repo_name_for_params(phab, repohost, url):
    """Return a sensible repo name from the given parameters.

    Usage examples:
        >>> _repo_name_for_params('phab', 'host', 'namespace/repo.1.git')
        'phab_host_namespace_repo-1'

    :phab: the string name of the phab config
    :repohost: the string name of the repository host
    :url: the relative url of the repository
    :returns: the string best-effort to name the repository config

    """
    no_dot_git_url = url[:-4] if url.endswith('.git') else url
    dot_to_dash = no_dot_git_url.replace(".", "-")
    snakecase_url = dot_to_dash.lower().replace("/", "_")

    name = "{phab}_{repohost}_{url}".format(
        phab=phab, repohost=repohost, url=snakecase_url)

    return name


def process(args):

    fs = abdt_fs.make_default_accessor()

    repo_name = args.name
    if repo_name is None:
        repo_name = _repo_name_for_params(
            args.phabricator_name, args.repohost_name, args.repo_url)

    repo_desc = args.repo_desc
    if repo_desc is None:
        repo_desc = _repo_desc_for_params(
            args.phabricator_name, args.repohost_name, args.repo_url)

    try_touch_path = fs.layout.repo_try(repo_name)
    ok_touch_path = fs.layout.repo_ok(repo_name)
    repo_path = fs.layout.repo(repo_name)

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
        repo_desc=repo_desc,
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

    # determine the repo push url from the parsed params
    repo_push_url = abdi_repoargs.get_repo_push_url(repo_params)

    with fs.lockfile_context():
        with abdi_repo.setup_repo_context(repo_url, repo_path, repo_push_url):
            fs.create_repo_config(repo_name, config)


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
