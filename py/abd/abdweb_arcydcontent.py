"""Render html to report the state of a running instance of Arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdweb_arcydcontent
#
# Public Functions:
#   render
#   render_stats
#   render_controls
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import abdt_arcydreporter


def _join_url(base_url, leaf):
    """Return the result of joining two parts of a url together.

    Usage Examples:

        >>> _join_url('http://example.com/', 'mypage/')
        'http://example.com/mypage/'

        >>> _join_url('http://example.com', 'mypage/')
        'http://example.com/mypage/'

    :base_url: the start of the new url
    :leaf: the end of the new url
    :returns: the joined url

    """
    return '/'.join([base_url.rstrip('/'), leaf])


def render(
        formatter,
        base_url,
        report,
        is_reset_scheduled,
        is_pause_scheduled):

    formatter.heading('arcyd')

    formatter.horizontal_rule()
    render_controls(is_reset_scheduled, is_pause_scheduled, formatter)
    formatter.horizontal_rule()

    status = report[abdt_arcydreporter.ARCYD_STATUS]
    formatter.text('status: {status}'.format(status=status))

    description = report[abdt_arcydreporter.ARCYD_STATUS_DESCRIPTION]
    if description:
        with formatter.singletag_context('div', class_='container'):
            with formatter.singletag_context('div', class_='redcard'):
                formatter.text(description)

    stats = report[abdt_arcydreporter.ARCYD_STATISTICS]
    render_stats(stats, formatter)

    repo = report[abdt_arcydreporter.ARCYD_CURRENT_REPO]
    if repo:
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
            formatter.link(_join_url(base_url, repo_name), repo_human_name)

    formatter.horizontal_rule()

    repos = report[abdt_arcydreporter.ARCYD_REPOS]
    for repo in repos:
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
            formatter.link(_join_url(base_url, repo_name), repo_human_name)


def render_stats(stats, formatter):
    current_duration = stats[abdt_arcydreporter.ARCYD_STAT_CURRENT_CYCLE_TIME]
    last_duration = stats[abdt_arcydreporter.ARCYD_STAT_LAST_CYCLE_TIME]
    tag_times = stats[abdt_arcydreporter.ARCYD_STAT_TAG_TIMES]
    if current_duration:
        formatter.text(
            'current cycle time: {:.2f} secs'.format(current_duration))
    if last_duration:
        formatter.text(
            'last cycle time: {:.2f} secs'.format(last_duration))
    if tag_times:
        for tag, time in tag_times.iteritems():
            formatter.text(
                '{tag} time: {time:.2f} secs'.format(tag=tag, time=time))


def render_controls(is_reset_scheduled, is_pause_scheduled, formatter):
    with formatter.tags_context('table'):
        with formatter.tags_context('tr'):
            with formatter.tags_context('td'):
                formatter.action_button(
                    'reset Arcyd', 'reset', not is_reset_scheduled)
            with formatter.tags_context('td'):
                formatter.action_button(
                    'cancel reset', 'cancel-reset', is_reset_scheduled)
        with formatter.tags_context('tr'):
            with formatter.tags_context('td'):
                formatter.action_button(
                    'pause Arcyd', 'pause', not is_pause_scheduled)
            with formatter.tags_context('td'):
                formatter.action_button(
                    'unpause Arcyd', 'unpause', is_pause_scheduled)


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
