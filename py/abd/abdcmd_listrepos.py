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
from __future__ import division
from __future__ import print_function

import abdi_repoargs
import abdt_fs


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '--only-formatted-repo-urls',
        action='store_true')


def process(args):
    fs = abdt_fs.make_default_accessor()

    with fs.lockfile_context():

        repo_config_path_list = fs.repo_config_path_list()
        repo_name_config_list = abdi_repoargs.parse_config_file_list(
            repo_config_path_list)

        for _, repo_config in repo_name_config_list:
            if args.only_formatted_repo_urls:
                print(abdi_repoargs.get_repo_url(repo_config))
            else:
                print(repo_config)


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
