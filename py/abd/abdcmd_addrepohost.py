"""Add a new repository host for the Arcyd instance to refer to."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_addrepohost
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

import abdt_fs


_CONFIG_REPO_URL_FORMAT = """
--repo-url-format
{repo_url_format}
""".strip()

_CONFIG_REPO_SNOOP_URL_FORMAT = """
--repo-snoop-url-format
{repo_snoop_url_format}
""".strip()

_CONFIG_BRANCH_URL_FORMAT = """
--branch-url-format
{branch_url_format}
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
        help="string name of the repohost, {regex}".format(
            regex=abdt_fs.CONFIG_NAME_REGEX))

    parser.add_argument(
        '--repo-url-format',
        metavar="STRING",
        type=str,
        default="{}",
        help="a python format() string to apply the '--repo-url' argument to "
             "produce the final url, e.g. 'http://github.com/{}.git'. the "
             "default is '{}' so the '--repo-url' is used unchanged.")

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

    parser.add_argument(
        '--admin-emails',
        nargs='*',
        metavar="TO",
        type=str,
        help="list of email addresses to send important repo events to")


def process(args):

    fs = abdt_fs.make_default_accessor()

    # generate the config file
    config = ""

    if args.repo_url_format:
        config = '\n'.join([
            config,
            _CONFIG_REPO_URL_FORMAT.format(
                repo_url_format=args.repo_url_format)])

    if args.repo_snoop_url_format:
        config = '\n'.join([
            config,
            _CONFIG_REPO_SNOOP_URL_FORMAT.format(
                repo_snoop_url_format=args.repo_snoop_url_format)])

    if args.branch_url_format:
        config = '\n'.join([
            config,
            _CONFIG_BRANCH_URL_FORMAT.format(
                branch_url_format=args.branch_url_format)])

    if args.admin_emails:
        config = '\n'.join([
            config,
            _CONFIG_ADMIN_EMAILS_FORMAT.format(
                admin_emails='\n'.join(args.admin_emails))])

    config = config.strip()

    # write out the config
    with fs.lockfile_context():
        fs.create_repohost_config(args.name, config)


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
