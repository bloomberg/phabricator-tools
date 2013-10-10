"""Report the state of a repository."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_reporeporter
#
# Public Classes:
#   SharedFileDictOutput
#    .write
#   SharedDictOutput
#    .write
#   RepoReporter
#    .on_tryloop_exception
#    .on_traceback
#    .on_completed
#    .start_branch
#    .no_users_on_branch
#    .finish_branch
#    .close
#
# Public Assignments:
#   REPO_ATTRIB_NAME
#   REPO_ATTRIB_STATUS
#   REPO_ATTRIB_STATUS_BRANCH
#   REPO_ATTRIB_STATUS_TEXT
#   REPO_LIST_ATTRIB
#   REPO_STATUS_UPDATING
#   REPO_STATUS_FAILED
#   REPO_STATUS_OK
#   REPO_STATUSES
#   RESULT_ATTRIB_BRANCHES
#   RESULT_BRANCH_NAME
#   RESULT_BRANCH_STATUS
#   RESULT_BRANCH_REVIEW_URL
#   RESULT_BRANCH_BRANCH_URL
#   RESULT_BRANCH_NOTES
#   RESULT_LIST_BRANCH
#   RESULT_BRANCH_STATUS_OK
#   RESULT_BRANCH_STATUS_BAD
#   RESULT_BRANCH_STATUS_UNKNOWN
#   RESULT_BRANCH_LIST_STATUS
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import json

import phlsys_fs

REPO_ATTRIB_NAME = 'name'
REPO_ATTRIB_STATUS = 'status'
REPO_ATTRIB_STATUS_BRANCH = 'status-current-branch'
REPO_ATTRIB_STATUS_TEXT = 'status-text'

REPO_LIST_ATTRIB = [
    REPO_ATTRIB_NAME,
    REPO_ATTRIB_STATUS,
    REPO_ATTRIB_STATUS_BRANCH,
    REPO_ATTRIB_STATUS_TEXT,
]

REPO_STATUS_UPDATING = 'updating'
REPO_STATUS_FAILED = 'failed'
REPO_STATUS_OK = 'ok'

REPO_STATUSES = [
    REPO_STATUS_UPDATING,
    REPO_STATUS_FAILED,
    REPO_STATUS_OK,
]

RESULT_ATTRIB_BRANCHES = 'branches'

RESULT_BRANCH_NAME = 'name'
RESULT_BRANCH_STATUS = 'status'
RESULT_BRANCH_REVIEW_URL = 'review-url'
RESULT_BRANCH_BRANCH_URL = 'branch-url'
RESULT_BRANCH_NOTES = 'notes'

RESULT_LIST_BRANCH = [
    RESULT_BRANCH_NAME,
    RESULT_BRANCH_STATUS,
    RESULT_BRANCH_REVIEW_URL,
    RESULT_BRANCH_BRANCH_URL,
    RESULT_BRANCH_NOTES,
]

RESULT_BRANCH_STATUS_OK = 'ok'
RESULT_BRANCH_STATUS_BAD = 'bad'
RESULT_BRANCH_STATUS_UNKNOWN = 'unknown'

RESULT_BRANCH_LIST_STATUS = [
    RESULT_BRANCH_STATUS_OK,
    RESULT_BRANCH_STATUS_BAD,
    RESULT_BRANCH_STATUS_UNKNOWN,
]


def _branch_status_to_string(status):
    if status is None:
        return RESULT_BRANCH_STATUS_UNKNOWN
    elif status:
        return RESULT_BRANCH_STATUS_OK
    return RESULT_BRANCH_STATUS_BAD


class SharedFileDictOutput(object):

    def __init__(self, filename):
        super(SharedFileDictOutput, self).__init__()
        self._filename = filename

    def write(self, d):
        assert isinstance(d, dict)
        with phlsys_fs.write_file_lock_context(self._filename) as f:
            f.write(json.dumps(d))


class SharedDictOutput(object):

    def __init__(self, shared_d):
        super(SharedDictOutput, self).__init__()
        self._shared_d = shared_d
        assert isinstance(self._shared_d, dict)

    def write(self, d):
        assert isinstance(d, dict)
        # copy contents to other dict
        self._shared_d.clear()
        self._shared_d.update(d)


def _exercise_branch_url_format_string(branch_format_string):
    """Exercise the supplied string so as to reveal defects early."""
    branch = 'blahbranch'
    branch_format_string.format(branch=branch)


def _exercise_review_url_format_string(review_format_string):
    """Exercise the supplied string so as to reveal defects early."""
    review = 123
    review_format_string.format(review=review)


class RepoReporter(object):

    def __init__(
            self,
            arcyd_reporter,
            repo,
            repo_name,
            review_url_format,
            branch_url_format,
            try_output,
            ok_output):
        """Initialise a new reporter to report to the specified outputs.

        :arcyd_reporter: reporter to escalate to
        :repo: machine-readable name to identify the repo
        :repo_name: human-readable name to identify the repo
        :review_url_format: format string for generating review urls
        :branch_url_format: format string for generating branch urls
        :try_output: output to use when trying the repo
        :ok_output: output to use when processed the repo

        """
        super(RepoReporter, self).__init__()
        self._arcyd_reporter = arcyd_reporter
        self._review_url_format = review_url_format
        self._branch_url_format = branch_url_format
        self._try_output = try_output
        self._ok_output = ok_output
        self._is_updating = True
        self._branches = []

        self._arcyd_reporter.start_repo(repo, repo_name)

        assert self._try_output
        assert self._ok_output

        self._repo_attribs = {
            REPO_ATTRIB_NAME: repo_name,
            REPO_ATTRIB_STATUS: '',
            REPO_ATTRIB_STATUS_BRANCH: '',
            REPO_ATTRIB_STATUS_TEXT: '',
        }

        self._branch_notes = None

        # make sure we've initialised all the expected attributes
        assert set(self._repo_attribs.keys()) == set(REPO_LIST_ATTRIB)

        if self._review_url_format:
            _exercise_review_url_format_string(self._review_url_format)
        if self._branch_url_format:
            _exercise_branch_url_format_string(self._branch_url_format)

        self._update_write_repo_status(REPO_STATUS_UPDATING)

    def on_tryloop_exception(self, e, delay):
        self._is_updating = False
        self._arcyd_reporter.on_tryloop_exception(e, delay)
        self._update_write_repo_status(
            REPO_STATUS_FAILED,
            str(e) + "\nwill wait " + str(delay))

    def on_traceback(self, traceback):
        self._is_updating = False
        self._update_write_repo_status(
            REPO_STATUS_FAILED,
            traceback)
        self._arcyd_reporter.fail_repo()

    def on_completed(self):
        self._is_updating = False
        self._update_write_repo_status(REPO_STATUS_OK)
        self._ok_output.write({
            RESULT_ATTRIB_BRANCHES: self._branches,
        })

    def start_branch(self, name):
        self._repo_attribs[REPO_ATTRIB_STATUS_BRANCH] = name
        self._branch_notes = ''

    def no_users_on_branch(self, emails):
        self._branch_notes += """Unable to assign any users to branch.

        These email addresses from authors of commits were considered:
        {emails}

        Note that the email address of the author in git must match one of the
        email addresses that the user has in Phabricator.

        You may use this to check your email address in Git, note that you
        should run this from your working copy or the ouput may not be correct.
        $ git config user.email

        See the "Pro Git" book for details on changing this config:
        http://git-scm.com/book/en/Getting-Started-First-Time-Git-Setup

        Each user may see their configured email addresses in Phabricator
        by visiting a link like this (substitute your own base url)
        https://my.phabricator.domain/settings/panel/email/

        Quick fix steps from your working copy, on the review branch:

        first, fix your email address:
        $ git config --global user.email 'EMAIL ADDRESS KNOWN TO PHABRICATOR'

        then either create an empty commit with the now correct email address:
        $ git commit --allow-empty --no-edit -m 'empty commit with real author'
        $ git push

        or, amend the last commit with correct email address:
        $ git commit --amend --reset-author
        $ git push --force

        """.format(emails=emails).strip() + '\n\n'

    def finish_branch(self, status, review_id):
        branch_name = self._repo_attribs[REPO_ATTRIB_STATUS_BRANCH]

        branch_url = ''
        review_url = ''
        if review_id is not None and self._review_url_format:
            review_url = self._review_url_format.format(review=int(review_id))
        if self._branch_url_format:
            branch_url = self._branch_url_format.format(branch=branch_name)

        status_str = _branch_status_to_string(status)
        d = {
            RESULT_BRANCH_NAME: branch_name,
            RESULT_BRANCH_STATUS: status_str,
            RESULT_BRANCH_REVIEW_URL: review_url,
            RESULT_BRANCH_BRANCH_URL: branch_url,
            RESULT_BRANCH_NOTES: self._branch_notes.strip(),
        }
        assert set(d.keys()) == set(RESULT_LIST_BRANCH)

        self._branches.append(d)
        self._repo_attribs[REPO_ATTRIB_STATUS_BRANCH] = ''
        self._branch_notes = ''

    def _update_write_repo_status(self, status, text=''):
        self._repo_attribs[REPO_ATTRIB_STATUS] = status
        self._repo_attribs[REPO_ATTRIB_STATUS_TEXT] = text
        self._try_output.write(self._repo_attribs)

    def close(self):
        """Close any resources associated with the report."""
        if self._is_updating:
            self._update_write_repo_status(REPO_STATUS_FAILED)
            self._arcyd_reporter.fail_repo()
        else:
            self._arcyd_reporter.finish_repo()


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
