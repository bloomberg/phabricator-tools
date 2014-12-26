"""Remove a repository from the Arcyd instance."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_rmrepo
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

import os
import shutil

import phlsys_pid

import abdi_repoargs
import abdt_fs


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        'name',
        type=str,
        metavar='STR',
        help="string identifier of the repository to remove.")

    parser.add_argument(
        '--lookup-url',
        action='store_true',
        help="treat 'name' as a full url and lookup the associated repo"
             "config. Fail if there is more than one repo with the same url.")


def _remove_file_ignore_fail(path):
    try:
        os.remove(path)
    except OSError as e:
        print("Warning, problem removing file '{}':".format(path))
        print("  {}".format(e))
        print()


def _remove_dir_ignore_fail(path):
    try:
        shutil.rmtree(path)
    except OSError as e:
        print("Warning, problem removing dir '{}':".format(path))
        print("  {}".format(e))
        print()


def process(args):

    fs = abdt_fs.make_default_accessor()

    with fs.lockfile_context():
        pid = fs.get_pid_or_none()
        if pid is not None and phlsys_pid.is_running(pid):
            raise Exception("cannot remove repo whilst arcyd is running.")

        repo_name = args.name
        if args.lookup_url:
            repo_name = _determine_name_from_url(fs, repo_name)

        _remove_file_ignore_fail(fs.layout.repo_try(repo_name))
        _remove_file_ignore_fail(fs.layout.repo_ok(repo_name))
        _remove_dir_ignore_fail(fs.layout.repo(repo_name))
        fs.remove_repo_config(repo_name)


def _determine_name_from_url(fs, repo_url):
    """Return the string name of the repository for 'repo_url' or raise.

    If there is not exactly one repository config that refers to 'repo_url'
    then raise.

    :fs: abdt_fs.Accessor to use to determine the repo name from the url
    :repo_url: string clone url of the repository we fetch from / push to
    :returns: string name of the matching config

    """
    repo_config_path_list = fs.repo_config_path_list()
    repo_name_config_list = abdi_repoargs.parse_config_file_list(
        repo_config_path_list)

    candidate_names = []

    for repo_name, repo_config in repo_name_config_list:
        url = abdi_repoargs.get_repo_url(repo_config)
        if repo_url == url:
            candidate_names.append(repo_name)

    if not candidate_names:
        raise Exception("url '{url}' didn't match any names".format(
            url=repo_url))

    if len(candidate_names) > 1:
        raise Exception("url '{url}' matches many names:\n{names}\n".format(
            url=repo_url,
            names=candidate_names))

    return candidate_names[0]


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
