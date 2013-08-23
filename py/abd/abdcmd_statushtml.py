"""Render status files as meaningful html to present to users."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_statushtml
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import contextlib
import json

import phlsys_fs

import abdt_reporeporter


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


class _HtmlPrinter(object):

    def _print_open_tag(self, tag):
        print '<' + tag + '>'

    def _print_close_tag(self, tag):
        print '</' + tag + '>'

    def print_text(self, text):
        print text

    @contextlib.contextmanager
    def tags_context(self, *tags):
        for tag in tags:
            self._print_open_tag(tag)

        try:
            yield
        finally:
            for tag in reversed(tags):
                self._print_close_tag(tag)


def _print_html(printer, repo_report, branch_report):
    with printer.tags_context('html', 'body'):

        if not repo_report and not branch_report:
            printer.print_text('repo has never been tried')
            return

        if repo_report:
            status = repo_report[abdt_reporeporter.RepoAttribs.status]
            printer.print_text('status: ' + status)


def process(args):
    print args
    repo_report = _read_json_file(args.repo_report_file)
    branch_report = _read_json_file(args.branches_report_file)
    _print_html(_HtmlPrinter(), repo_report, branch_report)


#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
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
#------------------------------- END-OF-FILE ----------------------------------
