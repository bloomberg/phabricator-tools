"""Render status files as meaningful html to present to users."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_repostatushtml
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#   render_content
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import json

import phlsys_fs

import abdweb_htmlformatter
import abdweb_page
import abdweb_repocontent


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        'repo_report_file',
        metavar="REPOREPORTFILE",
        type=str,
        help="path to the try file to render")
    parser.add_argument(
        'branches_report_file',
        metavar="BRANCHESREPORTFILE",
        type=str,
        help="path to the try file to render")


def _read_json_file(filename):
    result = None
    with phlsys_fs.read_file_lock_context(filename) as f:
        text = f.read()
        if text:
            result = json.loads(text)
    return result


def process(args):
    print render_content(
        args.repo_report_file, args.branches_report_file)


def render_content(repo_report_file, branches_report_file):
    formatter = abdweb_htmlformatter.HtmlFormatter()
    repo_report = _read_json_file(repo_report_file)
    branch_report = _read_json_file(branches_report_file)
    abdweb_repocontent.render(formatter, repo_report, branch_report)
    content = formatter.get_content()

    formatter = abdweb_htmlformatter.HtmlFormatter()
    abdweb_page.render(formatter, content)
    return formatter.get_content()


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
