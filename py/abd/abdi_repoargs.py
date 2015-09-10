"""Define the arguments for a single repository."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdi_repoargs
#
# Public Functions:
#   parse_config_file_list
#   validate_args
#   get_repo_url
#   get_repo_push_url
#   get_repo_snoop_url
#   setup_parser
#   setup_phab_parser
#   setup_repohost_parser
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse


def parse_config_file_list(repo_config_path_list):
    """Return a list of parsed configs fom supplied 'repo_config_path_list'.

    :repo_config_path_list: list of string paths to config files
    :returns: list of argparse namespaces resulting from parsing files

    """
    configs = []

    for repo_config_path in repo_config_path_list:
        parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
        setup_parser(parser)
        repo_config = parser.parse_args(['@' + repo_config_path])
        repo_name = repo_config_path.split('/')[-1]  # strip the path prefix
        repo_args = (repo_name, repo_config)
        validate_args(repo_args[1])
        configs.append(repo_args)

    return configs


def validate_args(args):
    """Raise if the supplied args are not valid.

    :args: the namespace returned from the argparse parser
    :returns: None

    """
    if not args.admin_emails:
        raise Exception(
            "no admin emails specified for {}".format(args.repo_desc))


def get_repo_url(args):
    """Return the fully expanded url for this repo.

    :args: the namespace returned from the argparse parser
    :returns: string url to clone the repo

    """
    return args.repo_url_format.format(args.repo_url)


def get_repo_push_url(args):
    """Return the fully expanded push url for this repo or None.

    :args: the namespace returned from the argparse parser
    :returns: string url to push the repo, or None

    """
    url = None
    if args.repo_push_url_format:
        url = args.repo_push_url_format.format(args.repo_url)
    return url


def get_repo_snoop_url(args):
    """Return the fully expanded url for snooping this repo or None.

    :args: the namespace returned from the argparse parser
    :returns: string url to snoop the repo, or None

    """
    url = None
    if args.repo_snoop_url_format:
        url = args.repo_snoop_url_format.format(args.repo_url)
    return url


def setup_parser(parser):
    setup_phab_parser(parser)
    setup_repohost_parser(parser)

    parser.add_argument(
        '--admin-emails',
        nargs='+',
        metavar="TO",
        action='append',
        type=str,
        help="list of email addresses to send important repo events to")

    parser.add_argument(
        '--repo-desc',
        metavar="DESC",
        type=str,
        required=True,
        help="description to use in emails")

    parser.add_argument(
        '--repo-path',
        metavar="PATH",
        type=str,
        required=True,
        help="path to the repository on disk")

    parser.add_argument(
        '--repo-url',
        metavar="URL",
        type=str,
        required=True,
        help="url to clone the repository, e.g. 'github:org/repo' or maybe "
             "something like 'org/repo' if using '--repo-url-format'.")

    parser.add_argument(
        '--try-touch-path',
        metavar="PATH",
        type=str,
        required=True,
        help="file to touch when trying to update a repo")

    parser.add_argument(
        '--ok-touch-path',
        metavar="PATH",
        type=str,
        required=True,
        help="file to touch when successfully updated a repo")


def setup_phab_parser(parser):

    parser.add_argument(
        '--instance-uri',
        type=str,
        metavar='ADDRESS',
        required=True,
        help="URI to use to access the conduit API, e.g. "
             "'http://127.0.0.1/api/'.")

    parser.add_argument(
        '--arcyd-user',
        type=str,
        metavar='USERNAME',
        required=True,
        help="username of admin account registered for arcyd to use.")

    parser.add_argument(
        '--arcyd-cert',
        metavar="CERT",
        type=str,
        required=True,
        help="Phabricator Conduit API certificate to use, this is the "
        "value that you will find in your user account in Phabricator "
        "at: http://your.server.example/settings/panel/conduit/. "
        "It can also be found in ~/.arcrc.")

    parser.add_argument(
        '--review-url-format',
        type=str,
        metavar='STRING',
        help="a format string for generating URLs for viewing reviews, e.g. "
             "something like this: "
             "'http://my.phabricator/D{review}' , "
             "note that the {review} will be substituted for the id of the "
             "branch.")

    parser.add_argument(
        '--https-proxy',
        metavar="PROXY",
        type=str,
        help="proxy URI for arcyd to use when connecting to conduit on https.")


def setup_repohost_parser(parser):

    parser.add_argument(
        '--repo-url-format',
        metavar="STRING",
        type=str,
        default="{}",
        help="a python format() string to apply the '--repo-url' argument to "
             "produce the final url, e.g. 'http://github.com/{}.git'. the "
             "default is '{}' so the '--repo-url' is used unchanged.")

    parser.add_argument(
        '--repo-push-url-format',
        metavar="STRING",
        type=str,
        help="a python format() string to apply the '--repo-url' "
             "argument to produce a push url, e.g. "
             "'http://github.com/{}.git'.")

    parser.add_argument(
        '--repo-snoop-url-format',
        metavar="URL",
        type=str,
        help="URL to use to snoop the latest contents of the repository, this "
             "is used by Arcyd to more efficiently determine if it needs to "
             "fetch the repository or not.  The efficiency comes from "
             "re-using connections to the same host when querying.  The "
             "contents returned by the URL are expected to change every time "
             "the git repository changes, a good example of a URL to supply "
             "is to the 'info/refs' address if you're serving up the repo "
             "over http or https.  "
             "e.g. 'http://server.test/git/{}/info/refs'. the {} will be "
             "substituted with the supplied '--repo-url' argument.'")

    parser.add_argument(
        '--branch-url-format',
        type=str,
        metavar='STRING',
        help="a format string for generating URLs for viewing branches, e.g. "
             "for a gitweb install: "
             "'http://my.git/gitweb?p={repo_url}.git"
             ";a=log;h=refs/heads/{branch}', "
             "note that the {branch} will be substituted for the branch name. "
             "note that the {repo_url} will be substituted for the supplied "
             "'--repo-url' argument. "
             "the result will be used on the dashboard to link to branches.")


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
