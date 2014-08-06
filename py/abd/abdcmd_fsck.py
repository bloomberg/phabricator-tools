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

import os

import phlgitx_ignoreident

import abdi_repo
import abdi_repoargs
import abdt_fs


def getFromfilePrefixChars():
    return None


def setupParser(parser):

    parser.add_argument(
        '--fix',
        action="store_true",
        help="resolve issues that are detected, where possible.")


def process(args):

    fs = abdt_fs.make_default_accessor()

    exit_code = 0

    with fs.lockfile_context():
        repo_config_path_list = fs.repo_config_path_list()

        if not _check_repo_config_path_list(repo_config_path_list):
            exit_code = 1

        repo_name_config_list = abdi_repoargs.parse_config_file_list(
            repo_config_path_list)

        if not _check_repo_name_config_list(args, repo_name_config_list):
            exit_code = 1

    if exit_code != 0 and not args.fix:
        print "use '--fix' to attempt to fix the issues"

    return exit_code


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
            print "'{}' is not a valid repo config name".format(
                repo_filename)
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

        if not _check_repo_cloned(args, repo_name, repo_config):
            all_ok = False
        else:
            if not _check_repo_ignoring_ident(args, repo_config):
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
        print "'{}' is missing repo '{}'".format(
            repo_name, repo_config.repo_path)
        if args.fix:
            repo_url = abdi_repoargs.get_repo_url(repo_config)
            print "cloning '{}' ..".format(repo_url)
            abdi_repo.setup_repo(repo_url, repo_config.repo_path)
        else:
            all_ok = False

    return all_ok


def _check_repo_ignoring_ident(args, repo_config):
    """Return False if the supplied repo isn't ignoring ident config.

    Will print details of errors found. Will continue when errors are found,
    unless they interfere with the operation of fsck.

    :args: argeparse arguments to arcyd fsck
    :repo_config: argparse namespace of the repo's config
    :returns: True or False

    """
    all_ok = True
    is_ignoring = phlgitx_ignoreident.is_repo_definitely_ignoring
    if not is_ignoring(repo_config.repo_path):
        print "'{}' is not ignoring ident attributes".format(
            repo_config.repo_path)
        if args.fix:
            print "setting {} to ignore ident ..".format(
                repo_config.repo_path)

            phlgitx_ignoreident.ensure_repo_ignoring(
                repo_config.repo_path)
        else:
            all_ok = False

    return all_ok


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
