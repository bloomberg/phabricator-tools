"""Provide useful utilities for formatting html."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdweb_htmlformatter
#
# Public Classes:
#   HtmlFormatter
#    .raw
#    .heading
#    .text
#    .get_content
#    .section_break
#    .horizontal_rule
#    .link
#    .table_from_tuple_list
#    .tags_context
#    .singletag_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import cgi
import contextlib


class HtmlFormatter(object):

    def __init__(self):
        super(HtmlFormatter, self).__init__()
        self._string = ''

    def _add_open_tag(self, tag):
        self.raw('<{}>'.format(tag))

    def _add_close_tag(self, tag):
        self.raw('</{}>'.format(tag))

    def raw(self, text):
        self._string += text

    def heading(self, text):
        with self.tags_context('h1'):
            self.raw(text)

    def text(self, text):
        with self.tags_context('pre'):
            self.raw(cgi.escape(text))

    def get_content(self):
        return self._string

    def section_break(self):
        self.raw('<br/>')

    def horizontal_rule(self):
        self.raw('<hr/>')

    def link(self, target, text=None):
        self._add_open_tag('a href={}'.format(target))
        if text:
            self.raw(text)
        else:
            self.raw(target)
        self._add_close_tag('a')

    def table_from_tuple_list(
            self, item_list, heading_list, format_list, class_):
        with self.singletag_context('table', class_=class_):
            with self.singletag_context('tr', class_=class_):
                for heading in heading_list:
                    with self.singletag_context('th', class_=class_):
                        self.raw(heading)
            for item in item_list:
                with self.singletag_context('tr', class_=class_):
                    for i, field in enumerate(item):
                        with self.singletag_context('td', class_=class_):
                            if field is not None:
                                self.raw(format_list[i].format(field))
                            else:
                                self.raw('None')

    @contextlib.contextmanager
    def tags_context(self, *tags):
        for tag in tags:
            self._add_open_tag(tag)

        try:
            yield
        finally:
            for tag in reversed(tags):
                self._add_close_tag(tag)

    @contextlib.contextmanager
    def singletag_context(self, tag, class_=None):
        if class_:
            self._add_open_tag("{tag} class='{class_}'".format(
                tag=tag, class_=class_))
        else:
            self._add_open_tag(tag)

        try:
            yield
        finally:
            self._add_close_tag(tag)


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
