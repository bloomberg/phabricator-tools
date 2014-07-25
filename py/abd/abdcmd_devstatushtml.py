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
import abdt_repooptions
import abdt_reporeporter
import abdt_shareddictoutput
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
        report)

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
        abdt_shareddictoutput.ToDict(report),
        "arcyd@localhost")

    arcyd_reporter.start_repo('name', 'human-name')

    config = abdt_repooptions.Data()
    config.branch_url_format = (
        'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}')
    config.review_url_format = 'http://my.phabricator/{review}'

    # simulate unhandled exception during processing repo

    reporter = abdt_reporeporter.RepoReporter(
        arcyd_reporter,
        "exception repo-machine-name",
        "exception repo",
        "exception_repo",
        abdt_shareddictoutput.ToDict(repo_report),
        abdt_shareddictoutput.ToDict(branch_report))

    reporter.set_config(config)

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
        "myorg/myrepo",
        abdt_shareddictoutput.ToDict(repo_report),
        abdt_shareddictoutput.ToDict(branch_report))

    reporter.set_config(config)

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
        abdt_shareddictoutput.ToDict(report),
        "arcyd@localhost")

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
        reporter.log_system_error('error', 'description of error')
        reporter.log_system_error('other-error', 'description of other error')
        reporter.start_repo('updating_repo-machine', 'updating_repo')
        reporter.log_user_action('createrev', 'user created 1231 from branch')
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
