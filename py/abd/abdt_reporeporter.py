"""Report the state of a repository."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_reporeporter
#
# Public Classes:
#   RepoReporter
#    .set_config
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


class RepoReporter(object):

    def __init__(
            self,
            arcyd_reporter,
            repo,
            repo_name,
            repo_url,
            try_output,
            ok_output):
        """Initialise a new reporter to report to the specified outputs.

        :arcyd_reporter: reporter to escalate to
        :repo: a machine-readable name to identify the repo
        :repo_name: human-readable name to identify the repo
        :repo_url: url to compose branch urls with
        :try_output: output to use when trying the repo
        :ok_output: output to use when processed the repo

        """
        super(RepoReporter, self).__init__()
        self._arcyd_reporter = arcyd_reporter
        self._repo_url = repo_url
        self._try_output = try_output
        self._ok_output = ok_output
        self._is_updating = True
        self._branches = []
        self._config = None

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

        self._update_write_repo_status(REPO_STATUS_UPDATING)

    def set_config(self, config):
        self._config = config

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

        If you want to / have to use a different email address to register
        with Phabricator then you will need to ensure the latest commit on
        your branch uses the same email address.

        Quick fix steps from your working copy, on the review branch:

        first, fix your email address:
        $ git config --global user.email 'EMAIL ADDRESS KNOWN TO PHABRICATOR'

        create an empty commit with the previous message but new author:
        $ git commit --reuse-message=HEAD --reset-author --allow-empty
        $ git push

        or, amend the last commit with correct email address:
        $ git commit --amend --reset-author
        $ git push --force

        """.format(emails=emails).strip() + '\n\n'

    def finish_branch(self, status, review_id):
        branch_name = self._repo_attribs[REPO_ATTRIB_STATUS_BRANCH]

        # fill in urls from pre-configured formats if possible
        branch_url = ''
        review_url = ''
        branch_fmt = self._config.branch_url_format if self._config else None
        review_fmt = self._config.review_url_format if self._config else None
        if branch_fmt:
            branch_url = branch_fmt.format(
                branch=branch_name, repo_url=self._repo_url)
        if review_id is not None and review_fmt:
            review_url = review_fmt.format(review=int(review_id))

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
