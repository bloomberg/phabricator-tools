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

import argparse
import os

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
        for repo in fs.repo_config_path_list():
            parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
            abdi_repoargs.setup_parser(parser)

            with open(repo) as f:
                repo_params = parser.parse_args(
                    line.strip() for line in f)

            if not os.path.isdir(repo_params.repo_path):
                print "'{}' is missing repo '{}'".format(
                    repo, repo_params.repo_path)
                if args.fix:
                    repo_url = abdi_repoargs.get_repo_url(repo_params)
                    print "cloning '{}' ..".format(repo_url)
                    abdi_repo.setup_repo(repo_url, repo_params.repo_path)
                else:
                    exit_code = 1

    if exit_code != 0 and not args.fix:
        print "use '--fix' to attempt to fix the issues"

    return exit_code


# -----------------------------------------------------------------------------
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
# ------------------------------ END-OF-FILE ----------------------------------
