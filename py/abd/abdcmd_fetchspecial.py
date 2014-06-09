"""Fetch the special refs for managed repos.

This can be useful if you are switching from one arcyd instance to
another, as arcyd will clobber the special refs each time it pushes.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_fetchspecial
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

import phlsys_git

import abdt_fs
import abdt_git


def getFromfilePrefixChars():
    return None


def setupParser(parser):

    selection_group = parser.add_mutually_exclusive_group(required=True)

    selection_group.add_argument(
        '--names',
        type=str,
        metavar='STR',
        nargs='+',
        help="string identifiers for the repositories, '[_a-zA-Z0-9]+'.")

    selection_group.add_argument(
        '--all',
        action='store_true',
        help="select all repositories.")


def process(args):

    fs = abdt_fs.make_default_accessor()

    repo_name_list = args.names

    if args.all:
        repo_name_list = fs.repo_name_list()

    for repo_name in repo_name_list:
        print repo_name
        repo_path = fs.layout.repo(repo_name)
        repo = phlsys_git.Repo(repo_path)
        abdt_git.checkout_master_fetch_special_refs(repo, 'origin')


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
