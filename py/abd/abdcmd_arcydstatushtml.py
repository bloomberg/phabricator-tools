"""Render arcyd status file as meaningful html to present to users."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_arcydstatushtml
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

import abdweb_arcydcontent
import abdweb_htmlformatter
import abdweb_page


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        'report_file',
        metavar="REPORTFILE",
        type=str,
        help="path to the file to render")
    parser.add_argument(
        'base_url',
        metavar="URL",
        type=str,
        help="base url to construct links from")


def _read_json_file(filename):
    result = None
    with phlsys_fs.read_file_lock_context(filename) as f:
        text = f.read()
        if text:
            result = json.loads(text)
    return result


def process(args):
    content = render_content(
        args.report_file, args.base_url)
    print content


def render_content(report_file, base_url):

    formatter = abdweb_htmlformatter.HtmlFormatter()
    report = _read_json_file(report_file)
    abdweb_arcydcontent.render(
        formatter,
        base_url,
        report)
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
