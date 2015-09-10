"""Check the Arcyd files for consistency and fix any issues."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_fsck
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

import phlgitx_ignoreattributes
import phlsys_git
import phlsys_pid
import phlsys_subprocess

import abdi_repo
import abdi_repoargs
import abdt_fs


def getFromfilePrefixChars():
    return None


def setupParser(parser):

    parser.add_argument(
        '--repos',
        nargs='*',
        help="an optional list of repository names to check.")

    parser.add_argument(
        '--fix',
        action="store_true",
        help="resolve issues that are detected, where possible.")

    parser.add_argument(
        '--remote',
        action="store_true",
        help="also check remote resources pointed to by the file system. e.g. "
             "git remotes.")

    parser.add_argument(
        '--verbose', '-v',
        action="store_true",
        help="verbose output.")


def process(args):

    fs = abdt_fs.make_default_accessor()

    exit_code = 0

    with fs.lockfile_context():
        pid = fs.get_pid_or_none()
        if pid is not None and phlsys_pid.is_running(pid):
            raise Exception("cannot fsck whilst arcyd is running.")

        repo_config_path_list = _determine_repo_config_path_list(
            fs, args.repos)

        if not _check_repo_config_path_list(repo_config_path_list):
            exit_code = 1

        repo_name_config_list = abdi_repoargs.parse_config_file_list(
            repo_config_path_list)

        if not _check_repo_name_config_list(args, repo_name_config_list):
            exit_code = 1

    if exit_code != 0 and not args.fix:
        print("use '--fix' to attempt to fix the issues")

    return exit_code


def _determine_repo_config_path_list(fs, user_repo_names):
    all_repo_paths = fs.repo_config_path_list()
    if user_repo_names is None:
        return all_repo_paths
    else:
        user_repo_paths = [fs.layout.repo_config(n) for n in user_repo_names]
        unknown_paths = set(user_repo_paths) - set(all_repo_paths)
        if not user_repo_names:
            raise Exception("no repos specified")
        if unknown_paths:
            raise Exception("unknown repos: {}".format(unknown_paths))
        return user_repo_paths


def _check_repo_config_path_list(repo_config_path_list):
    """Return False if any errors are detected in the supplied list.

    Will print details of errors found and continue.

    :repo_config_path_list: a list of paths to repo configs
    :returns: True or False

    """
    all_ok = True
    for repo_config_path in repo_config_path_list:
        repo_filename = os.path.basename(repo_config_path)
        if not abdt_fs.is_config_name_valid(repo_filename):
            print("'{}' is not a valid repo config name".format(
                repo_filename))
            all_ok = False

    return all_ok


def _check_repo_name_config_list(args, repo_name_config_list):
    """Return False if any errors are detected in the supplied list.

    Will print details of errors found. Will continue when errors are found,
    unless they interfere with the operation of fsck.

    :args: argeparse arguments to arcyd fsck
    :repo_config_path_list: a list of paths to repo configs
    :returns: True or False

    """
    all_ok = True
    for repo_name, repo_config in repo_name_config_list:

        if args.verbose:
            print("Checking", repo_name)

        if not _check_repo_cloned(args, repo_name, repo_config):
            all_ok = False
        else:
            if not _check_repo_ignoring_attributes(args, repo_config):
                all_ok = False
            if args.remote:
                if not _check_repo_remote(args, repo_name, repo_config):
                    all_ok = False

    return all_ok


def _check_repo_cloned(args, repo_name, repo_config):
    """Return False if the supplied repo isn't cloned or fixed.

    Will print details of errors found. Will continue when errors are found,
    unless they interfere with the operation of fsck.

    :args: argeparse arguments to arcyd fsck
    :repo_name: string name of the repository
    :repo_config: argparse namespace of the repo's config
    :returns: True or False

    """
    all_ok = True
    if not os.path.isdir(repo_config.repo_path):
        print("'{}' is missing repo '{}'".format(
            repo_name, repo_config.repo_path))
        if args.fix:
            repo_url = abdi_repoargs.get_repo_url(repo_config)
            repo_push_url = abdi_repoargs.get_repo_push_url(repo_config)
            print("cloning '{}' ..".format(repo_url))
            abdi_repo.setup_repo(
                repo_url, repo_config.repo_path, repo_push_url)
        else:
            all_ok = False

    return all_ok


def _check_repo_ignoring_attributes(args, repo_config):
    """Return False if the supplied repo isn't ignoring attributes config.

    Will print details of errors found. Will continue when errors are found,
    unless they interfere with the operation of fsck.

    :args: argeparse arguments to arcyd fsck
    :repo_config: argparse namespace of the repo's config
    :returns: True or False

    """
    all_ok = True
    is_ignoring = phlgitx_ignoreattributes.is_repo_definitely_ignoring
    if not is_ignoring(repo_config.repo_path):
        print("'{}' is not ignoring some attributes".format(
            repo_config.repo_path))
        if args.fix:
            print("setting {} to ignore some attributes ..".format(
                repo_config.repo_path))

            phlgitx_ignoreattributes.ensure_repo_ignoring(
                repo_config.repo_path)
        else:
            all_ok = False

    return all_ok


def _check_repo_remote(args, repo_name, repo_config):
    """Return False if the supplied repo has problems with it's remote.

    Will print details of errors found. Will continue when errors are found,
    unless they interfere with the operation of fsck.

    :args: argeparse arguments to arcyd fsck
    :repo_name: string name of the repository
    :repo_config: argparse namespace of the repo's config
    :returns: True or False

    """
    all_ok = True
    repo = phlsys_git.Repo(repo_config.repo_path)

    # check that we can read from the remote
    try:
        repo("ls-remote")
    except phlsys_subprocess.CalledProcessError as e:
        all_ok = False
        print("error reading remote for {repo}".format(repo=repo_name))
        _print_indented(4, e.stdout)
        _print_indented(4, e.stderr)
        print()

    # check that we can write to the remote
    try:
        abdi_repo.try_push_special_refs(repo)
    except phlsys_subprocess.CalledProcessError as e:
        all_ok = False
        print("error writing remote for {repo}".format(repo=repo_name))
        _print_indented(4, e.stdout)
        _print_indented(4, e.stderr)
        print()

    # ensure the reserve branch
    try:
        if not abdi_repo.is_remote_reserve_branch_present(repo):
            print("'{repo}' has no reserve branch".format(repo=repo_name))
            if args.fix:
                print("ensuring reserve branch for '{repo}'..".format(
                    repo=repo_name))
                abdi_repo.ensure_reserve_branch(repo)
            else:
                all_ok = False
    except phlsys_subprocess.CalledProcessError as e:
        all_ok = False
        print(
            "error ensuring reserve branch for {repo}".format(repo=repo_name))
        _print_indented(4, e.stdout)
        _print_indented(4, e.stderr)
        print()

    # ensure the vestigial landinglog ref is not present
    try:
        if abdi_repo.is_legacy_landinglog_branch_present(repo):
            print("'{repo}' has legacy landinglog".format(repo=repo_name))
            if args.fix:
                print("removing landinglog for '{repo}'..".format(
                    repo=repo_name))
                abdi_repo.remove_landinglog(repo)
            else:
                all_ok = False
    except phlsys_subprocess.CalledProcessError as e:
        all_ok = False
        print("error removing landinglog for {repo}".format(repo=repo_name))
        _print_indented(4, e.stdout)
        _print_indented(4, e.stderr)
        print()

    return all_ok


def _print_indented(spaces, s):
    """Print the supplied string 's' with each line indented by 'spaces'.

    :spaces: the integer number of spaces to prepend
    :s: the string to indent
    :returns: None

    """
    for line in s.splitlines():
        print("{indent}{line}".format(
            indent=" " * spaces,
            line=line))


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
