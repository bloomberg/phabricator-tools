"""Help develop status pages by providing simulating various statuses."""
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

import abdt_arcydreporter
import abdt_reporeporter
import abdweb_arcydcontent
import abdweb_htmlformatter
import abdweb_page
import abdweb_repocontent


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    pass


def _write_repo_status_page(filename, repo_report, branch_report):

    filename += '.html'

    formatter = abdweb_htmlformatter.HtmlFormatter()
    abdweb_repocontent.render(formatter, repo_report, branch_report)
    content = formatter.get_content()

    formatter = abdweb_htmlformatter.HtmlFormatter()
    abdweb_page.render(formatter, content)

    with open(filename, 'w') as f:
        f.write(formatter.get_content())
    print "wrote:", filename


def _write_arcyd_status_page(filename, report):

    filename += '.html'

    formatter = abdweb_htmlformatter.HtmlFormatter()
    abdweb_arcydcontent.render(
        formatter,
        'https://server.test/',
        report,
        is_reset_scheduled=False,
        is_pause_scheduled=False)

    content = formatter.get_content()

    formatter = abdweb_htmlformatter.HtmlFormatter()
    abdweb_page.render(formatter, content)

    with open(filename, 'w') as f:
        f.write(formatter.get_content())
    print "wrote:", filename


def _exercise_reporeporter():

    repo_report = {}
    branch_report = {}

    def _write(filename):
        _write_repo_status_page(filename, repo_report, branch_report)

    report = {}
    arcyd_reporter = abdt_arcydreporter.ArcydReporter(
        abdt_arcydreporter.SharedDictOutput(report))

    arcyd_reporter.start_repo('name', 'human-name')

    # simulate unhandled exception during processing repo

    reporter = abdt_reporeporter.RepoReporter(
        arcyd_reporter,
        "exception repo-machine-name",
        "exception repo",
        'http://my.phabricator/{review}',
        'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}',
        abdt_reporeporter.SharedDictOutput(repo_report),
        abdt_reporeporter.SharedDictOutput(branch_report))

    with contextlib.closing(reporter):
        _write('updating')
        reporter.start_branch('mybranch')
        reporter.on_traceback('traceback\ntraceback\n')
    _write('exception_closed')

    # simulate repo with no problems

    repo_report = {}
    branch_report = {}

    reporter = abdt_reporeporter.RepoReporter(
        arcyd_reporter,
        "myrepo-machine-name",
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


def _exercise_arcydreporter():

    report = {}

    def _write(filename):
        _write_arcyd_status_page(filename, report)

    # simulate unhandled exception during processing repo

    reporter = abdt_arcydreporter.ArcydReporter(
        abdt_arcydreporter.SharedDictOutput(report))

    with contextlib.closing(reporter):
        _write('arcyd_exception_start')
        reporter.start_repo('myrepo-machine', 'myrepo')
        _write('arcyd_exception_startrepo')
        with reporter.tag_timer_context('git'):
            pass
        with reporter.tag_timer_context('phabricator'):
            pass
        reporter.finish_repo()
        reporter.start_repo('repeatrepo-machine', 'repeatrepo')
        reporter.finish_repo()
        reporter.start_repo('myrepo2-machine', 'myrepo2')
        reporter.finish_repo()
        reporter.start_repo('myrepo3-machine', 'myrepo3')
        reporter.finish_repo()
        reporter.start_repo('failrepo-machine', 'failrepo')
        reporter.fail_repo()
        reporter.start_repo('myrepo4-machine', 'myrepo4')
        reporter.finish_repo()
        reporter.start_repo('repeatrepo-machine', 'repeatrepo')
        reporter.finish_repo()
        reporter.start_repo('updating_repo-machine', 'updating_repo')
        _write('arcyd_many_repos')
        reporter.finish_repo()
        reporter.start_sleep(3)
        _write('arcyd_sleeping')
        reporter.finish_sleep()
        _write('arcyd_idle')
        reporter.on_tryloop_exception('exception', 'delay')
        _write('arcyd_tryloop_exception')
    _write('arcyd_stopped')


def process(args):

    _ = args  # NOQA
    _exercise_arcydreporter()
    _exercise_reporeporter()

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
