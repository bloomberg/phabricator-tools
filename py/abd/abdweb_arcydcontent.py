"""Render html to report the state of a running instance of Arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdweb_arcydcontent
#
# Public Functions:
#   render
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
from __future__ import absolute_import

import phlurl_request

import abdt_arcydreporter


def render(
        formatter,
        base_url,
        report):

    formatter.heading('arcyd')

    formatter.horizontal_rule()

    status = report[abdt_arcydreporter.ARCYD_STATUS]
    stats = report[abdt_arcydreporter.ARCYD_STATISTICS]
    description = report[abdt_arcydreporter.ARCYD_STATUS_DESCRIPTION]
    _render_status(status, stats, formatter, description)

    repo = report[abdt_arcydreporter.ARCYD_CURRENT_REPO]
    if repo:
        _render_repo(base_url, repo, formatter)

    formatter.horizontal_rule()

    repos = report[abdt_arcydreporter.ARCYD_REPOS]
    with formatter.singletag_context('div', class_='container'):
        sorted_repos = sorted(
            repos, key=lambda x: x[abdt_arcydreporter.REPO_ATTRIB_HUMAN_NAME])

        for repo in sorted_repos:
            _render_repo(base_url, repo, formatter)

    log_system_error = report[abdt_arcydreporter.ARCYD_LOG_SYSTEM_ERROR]
    if log_system_error:
        formatter.horizontal_rule()
        _render_error_log('recent system errors', log_system_error, formatter)

    log_user_action = report[abdt_arcydreporter.ARCYD_LOG_USER_ACTION]
    if log_user_action:
        formatter.horizontal_rule()
        _render_info_log('recent user actions', log_user_action, formatter)

    formatter.horizontal_rule()
    _render_stats(stats, formatter)


def _render_status(status, stats, formatter, description):
    this_duration = stats[abdt_arcydreporter.ARCYD_STAT_CURRENT_CYCLE_TIME]
    last_duration = stats[abdt_arcydreporter.ARCYD_STAT_LAST_CYCLE_TIME]
    if this_duration and last_duration:
        if this_duration > last_duration:
            formatter.heading('this cycle: {:.2f} secs'.format(this_duration))
        else:
            formatter.heading('last cycle: {:.2f} secs'.format(last_duration))
    elif this_duration:
        formatter.heading('this cycle: {:.2f} secs'.format(this_duration))
    elif last_duration:
        formatter.heading('last cycle: {:.2f} secs'.format(last_duration))
    if status:
        formatter.text('status: {status}'.format(status=status))
    if description:
        with formatter.singletag_context('div', class_='container'):
            with formatter.singletag_context('div', class_='redcard'):
                formatter.text(description)


def _render_repo(base_url, repo, formatter):
    repo_name = repo[abdt_arcydreporter.REPO_ATTRIB_NAME]
    repo_human_name = repo[abdt_arcydreporter.REPO_ATTRIB_HUMAN_NAME]
    repo_status = repo[abdt_arcydreporter.REPO_ATTRIB_STATUS]

    if repo_status == abdt_arcydreporter.REPO_STATUS_OK:
        divclass = 'greencard'
    elif repo_status == abdt_arcydreporter.REPO_STATUS_UPDATING:
        divclass = 'activeinset'
    else:
        divclass = 'redcard'

    with formatter.singletag_context('div', class_=divclass):
        formatter.link(phlurl_request.join_url(
            base_url, repo_name), repo_human_name)


def _render_stats(stats, formatter):
    current_duration = stats[abdt_arcydreporter.ARCYD_STAT_CURRENT_CYCLE_TIME]
    last_duration = stats[abdt_arcydreporter.ARCYD_STAT_LAST_CYCLE_TIME]
    tag_samplers = stats[abdt_arcydreporter.ARCYD_STAT_TAG_SAMPLERS]

    if current_duration or last_duration or tag_samplers:
        formatter.heading('stats')

    if current_duration:
        formatter.text(
            'current cycle time: {:.2f} secs'.format(current_duration))

    if last_duration:
        formatter.text(
            'last cycle time: {:.2f} secs'.format(last_duration))

    if tag_samplers:
        Sampler = abdt_arcydreporter.Sampler.from_dict
        samplers_tags = [(Sampler(s), t) for t, s in tag_samplers.iteritems()]
        stats_tags = [
            (
                s.total,
                t,
                s.times,
                s.least,
                s.mean,
                s.most,
                s.last,
            )
            for s, t in samplers_tags
        ]

        heading_format = (
            ('total time', '{:.2f} secs'),
            ('tag', '{}'),
            ('count', '{}'),
            ('min', '{:.2f} secs'),
            ('mean', '{:.2f} secs'),
            ('max', '{:.2f} secs'),
            ('last', '{:.2f} secs'),
        )

        stats_tags.sort()
        stats_tags.reverse()

        formatter.table_from_tuple_list(
            stats_tags,
            [i[0] for i in heading_format],
            [i[1] for i in heading_format],
            'stats')


def _render_error_log(name, item_list, formatter):
    formatter.heading(name)
    with formatter.singletag_context('div', class_='container'):
        for item in reversed(item_list):
            with formatter.singletag_context('div', class_='redcard'):
                time = item[abdt_arcydreporter.ARCYD_LOGITEM_DATETIME]
                identifier = item[abdt_arcydreporter.ARCYD_LOGITEM_IDENTIFIER]
                detail = item[abdt_arcydreporter.ARCYD_LOGITEM_DETAIL]
                formatter.heading(identifier)
                formatter.text("{time} UTC".format(time=time))
                formatter.text(detail)


def _render_info_log(name, item_list, formatter):
    formatter.heading(name)
    with formatter.singletag_context('div', class_='container'):
        for item in reversed(item_list):
            with formatter.singletag_context('div', class_='bluecard'):
                detail = item[abdt_arcydreporter.ARCYD_LOGITEM_DETAIL]
                formatter.raw(detail)


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
