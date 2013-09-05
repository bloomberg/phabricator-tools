"""Help develop status-html by providing flags to simulate various statuses."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_devstatushtml
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import textwrap

import abdt_reporeporter
import abdweb_htmlformatter
import abdweb_page
import abdweb_repocontent


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    statuses = abdt_reporeporter.REPO_STATUSES
    status_group = parser.add_argument_group(
        'status arguments',
        'use one of ' + textwrap.fill(str(statuses)))

    status_group.add_argument(
        '--status',
        metavar="STATUS",
        required=True,
        choices=statuses)


def process(args):

    repo_report = {abdt_reporeporter.RepoAttribs.status: args.status}
    branch_report = {}

    formatter = abdweb_htmlformatter.HtmlFormatter()
    abdweb_repocontent.render(formatter, repo_report, branch_report)
    content = formatter.get_content()

    formatter = abdweb_htmlformatter.HtmlFormatter()
    abdweb_page.render(formatter, content)
    print formatter.get_content()


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
