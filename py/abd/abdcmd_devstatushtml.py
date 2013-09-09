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

from __future__ import absolute_import

import contextlib

import abdt_reporeporter
import abdweb_htmlformatter
import abdweb_page
import abdweb_repocontent


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    pass


def _write_status_page(filename, repo_report, branch_report):

    filename += '.html'

    formatter = abdweb_htmlformatter.HtmlFormatter()
    abdweb_repocontent.render(formatter, repo_report, branch_report)
    content = formatter.get_content()

    formatter = abdweb_htmlformatter.HtmlFormatter()
    abdweb_page.render(formatter, content)

    with open(filename, 'w') as f:
        f.write(formatter.get_content())
    print "wrote:", filename


def process(args):

    _ = args  # NOQA

    repo_report = {}
    branch_report = {}

    def _write(filename):
        _write_status_page(filename, repo_report, branch_report)

    # simulate unhandled exception during processing

    reporter = abdt_reporeporter.RepoReporter(
        "exception repo",
        'http://my.phabricator/{review}',
        'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}',
        abdt_reporeporter.SharedDictOutput(repo_report),
        abdt_reporeporter.SharedDictOutput(branch_report))

    with contextlib.closing(reporter):
        _write('exception_start')
        reporter.start_branch('mybranch')
        reporter.on_traceback('traceback\ntraceback\n')
    _write('exception_closed')

    # simulate repo with no problems

    repo_report = {}
    branch_report = {}

    reporter = abdt_reporeporter.RepoReporter(
        "myrepo",
        'http://my.phabricator/{review}',
        'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}',
        abdt_reporeporter.SharedDictOutput(repo_report),
        abdt_reporeporter.SharedDictOutput(branch_report))

    with contextlib.closing(reporter):
        reporter.start_branch('mybranch')
        reporter.finish_branch(True, None)
        reporter.start_branch('mybranch2')
        reporter.finish_branch(False, None)
        reporter.start_branch('mybranch3')
        reporter.finish_branch(None, None)
        reporter.start_branch('mybranch4')
        reporter.finish_branch(True, 1)
        reporter.start_branch('mybranch5')
        reporter.finish_branch(False, 2)
        reporter.start_branch('mybranch6')
        reporter.finish_branch(None, 3)

        reporter.start_branch('mybranch7')
        reporter.no_users_on_branch([])
        reporter.finish_branch(False, 4)
        reporter.start_branch('mybranch8')
        reporter.no_users_on_branch(set(['a@b.com', 'c@d.com']))
        reporter.finish_branch(False, 5)
        reporter.on_completed()
    _write('aok_closed')


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
