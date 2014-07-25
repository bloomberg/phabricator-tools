"""Test suite for phlsys_textconvert."""

from __future__ import absolute_import

import string
import unittest

import phlsys_textconvert


class Test(unittest.TestCase):

    def _check_unicode_to_ascii(self, src, dst):
        value = phlsys_textconvert.lossy_unicode_to_ascii(src)
        self.assertEqual(value, dst)
        self.assertIsInstance(value, type(dst))

    def test_empty(self):
        self._check_unicode_to_ascii(u"", "")

    def test_ascii_printable(self):
        self._check_unicode_to_ascii(
            unicode(string.printable),
            str(string.printable))

    def test_trailing_leading_space(self):
        self._check_unicode_to_ascii(u"trailing  ", "trailing  ")
        self._check_unicode_to_ascii(u"  leading", "  leading")
        self._check_unicode_to_ascii(u"trailing\t\t", "trailing\t\t")
        self._check_unicode_to_ascii(u"\t\tleading", "\t\tleading")

    def test_newlines(self):
        self._check_unicode_to_ascii(u"new\nline", "new\nline")
        self._check_unicode_to_ascii(u"windows\r\nline", "windows\r\nline")
        self._check_unicode_to_ascii(u"\nline", "\nline")
        self._check_unicode_to_ascii(u"\r\nline", "\r\nline")
        self._check_unicode_to_ascii(u"new\n", "new\n")
        self._check_unicode_to_ascii(u"windows\r\n", "windows\r\n")

    def test_nuls(self):
        self._check_unicode_to_ascii(u"nul\0middle", "nul\0middle")
        self._check_unicode_to_ascii(u"nul-end\0", "nul-end\0")
        self._check_unicode_to_ascii(u"\0nul-start", "\0nul-start")

    def test_ellipses(self):
        self._check_unicode_to_ascii(u"time passed\u2026", "time passed...")

    def test_hyphenation_point(self):
        self._check_unicode_to_ascii(u"hy\u2027phen\u2027ate", "hy?phen?ate")

    def test_dashes(self):
        self._check_unicode_to_ascii(u"\u2010", "-")
        self._check_unicode_to_ascii(u"\u2011", "-")
        self._check_unicode_to_ascii(u"\u2013", "-")
        self._check_unicode_to_ascii(u"\u2013", "-")
        self._check_unicode_to_ascii(u"\u2014", "-")
        self._check_unicode_to_ascii(u"\u2015", "-")
        self._check_unicode_to_ascii(u"\u2212", "-")

    def test_quotes(self):
        self._check_unicode_to_ascii(u"\u00b4", "'")
        self._check_unicode_to_ascii(u"\u2018", "'")
        self._check_unicode_to_ascii(u"\u2019", "'")
        self._check_unicode_to_ascii(u"\u201c", '"')
        self._check_unicode_to_ascii(u"\u201d", '"')

    def test_bullets(self):
        self._check_unicode_to_ascii(u"\u00b7", "*")
        self._check_unicode_to_ascii(u"\u2022", "*")
        self._check_unicode_to_ascii(u"\u2023", ">")
        self._check_unicode_to_ascii(u"\u2024", "*")
        self._check_unicode_to_ascii(u"\u2043", "-")
        self._check_unicode_to_ascii(u"\u25b8", ">")
        self._check_unicode_to_ascii(u"\u25e6", "o")

    def test_A_Breathing(self):

        # test we can convert unicode to unicode
        phlsys_textconvert.to_unicode(unicode('hello'))

        # test we can convert str to unicode
        self.assertIsInstance(
            phlsys_textconvert.to_unicode('hello'),
            unicode)

        # test invalid characters get replaced by the replacement character
        self.assertEqual(
            phlsys_textconvert.to_unicode('\xFF'),
            u'\uFFFD')

        # test 'horizontal ellipses' as UTF8 get replaced
        self.assertEqual(
            phlsys_textconvert.to_unicode('\xe2\x80\xa6'),
            u'\uFFFD\uFFFD\uFFFD')

        # test we can convert ascii to ascii
        phlsys_textconvert.ensure_ascii('hello')

        # test str stays str
        self.assertIsInstance(
            phlsys_textconvert.ensure_ascii('hello'),
            str)

        # test invalid characters get replaced by '?'
        self.assertEqual(
            phlsys_textconvert.ensure_ascii('\xFF'),
            '?')

        # test 'horizontal ellipses' as UTF8 get replaced
        self.assertEqual(
            phlsys_textconvert.ensure_ascii('\xe2\x80\xa6'),
            '???')


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
