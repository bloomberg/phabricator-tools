"""Provide useful utilities for formatting html."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdweb_htmlformatter
#
# Public Classes:
#   HtmlFormatter
#    .raw
#    .text
#    .get_content
#    .tags_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

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

    def text(self, text):
        self.raw(text)

    def get_content(self):
        return self._string

    @contextlib.contextmanager
    def tags_context(self, *tags):
        for tag in tags:
            self._add_open_tag(tag)

        try:
            yield
        finally:
            for tag in reversed(tags):
                self._add_close_tag(tag)


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
