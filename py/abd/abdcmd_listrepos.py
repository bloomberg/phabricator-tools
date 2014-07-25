"""List the repositories managed by this arcyd instance."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_listrepos
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

import abdi_repoargs
import abdt_fs


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--only-formatted-repo-urls',
        action='store_true')


# XXX: this probably belongs somewhere else, for re-use
def _iter_repo_args(abdt_accessor):
    for repo_path in abdt_accessor.repo_config_path_list():
        parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
        abdi_repoargs.setup_parser(parser)
        yield parser.parse_args(['@{}'.format(repo_path)])


def process(args):
    fs = abdt_fs.make_default_accessor()

    with fs.lockfile_context():
        for repo_args in _iter_repo_args(fs):
            if args.only_formatted_repo_urls:
                print abdi_repoargs.get_repo_url(repo_args)
            else:
                print repo_args


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
