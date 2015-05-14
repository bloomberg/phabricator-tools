"""create a diff from a git repository, reducing the diff if it is too big.
Automatic size reduction is achieved by discarding context.
`git-diff-helper` will call `git diff BASE...HEAD` on your behalf.

usage examples:

    $ arcyon git-diff-helper 3aad31 4def41

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# aoncmd_gitdiffhelper
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
import sys

import abdt_branch
import abdt_differ
import phlsys_git


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        'base',
        type=str,
        help="the base commit of the diff")
    parser.add_argument(
        'head',
        type=str,
        help="the head commit of the diff")


def process(args):
    repo_path = os.path.abspath(os.curdir)
    base = args.base
    head = args.head

    repo = phlsys_git.Repo(repo_path)
    # TODO: do not use private variable abdt_branch._MAX_DIFF_SIZE
    diff = abdt_differ.make_raw_diff(
        repo, base, head, abdt_branch._MAX_DIFF_SIZE)
    sys.stdout.write(diff.diff)


# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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
