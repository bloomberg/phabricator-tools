"""Render html to report the state of a repository watched by Arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdweb_repocontent
#
# Public Functions:
#   render
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import abdt_reporeporter


def render(formatter, repo_report, branch_report):

    if not repo_report and not branch_report:
        formatter.text('repo has never been tried')
        return

    _render_repo_report(formatter, repo_report)
    formatter.section_break()
    formatter.horizontal_rule()
    _render_branch_report(formatter, branch_report)


def _render_repo_report(formatter, repo_report):
    if not repo_report:
        return

    repo_name = repo_report[abdt_reporeporter.REPO_ATTRIB_NAME]
    status = repo_report[abdt_reporeporter.REPO_ATTRIB_STATUS]
    branch = repo_report[abdt_reporeporter.REPO_ATTRIB_STATUS_BRANCH]
    status_text = repo_report[abdt_reporeporter.REPO_ATTRIB_STATUS_TEXT]

    formatter.heading(repo_name)

    if status == abdt_reporeporter.REPO_STATUS_OK:
        divclass = 'greeninset'
    elif status == abdt_reporeporter.REPO_STATUS_UPDATING:
        divclass = 'activeinset'
    else:
        divclass = 'redinset'

    with formatter.singletag_context('div', class_=divclass):
        formatter.text('repo status: ' + status)
        if branch:
            formatter.text('branch: ' + branch)
        if status_text:
            formatter.text('status text:\n' + status_text)


def _render_branch_report(formatter, branch_report):
    if not branch_report:
        return

    branches = branch_report[abdt_reporeporter.RESULT_ATTRIB_BRANCHES]
    for branch in branches:
        name = branch[abdt_reporeporter.RESULT_BRANCH_NAME]
        status = branch[abdt_reporeporter.RESULT_BRANCH_STATUS]
        branch_url = branch[abdt_reporeporter.RESULT_BRANCH_BRANCH_URL]
        review_url = branch[abdt_reporeporter.RESULT_BRANCH_REVIEW_URL]
        notes = branch[abdt_reporeporter.RESULT_BRANCH_NOTES]

        if status == abdt_reporeporter.RESULT_BRANCH_STATUS_OK:
            divclass = 'greencard'
        else:
            divclass = 'redcard'

        with formatter.singletag_context('div', class_=divclass):
            formatter.heading(name)
            if branch_url:
                formatter.link(branch_url, 'view branch')
                formatter.section_break()
            if review_url:
                formatter.link(review_url, 'view review')
                formatter.section_break()
            if notes:
                formatter.text(notes)


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
