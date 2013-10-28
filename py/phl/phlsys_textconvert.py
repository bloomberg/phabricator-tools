"""Convert between unicode and ascii easily."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_textconvert
#
# Public Functions:
#   lossy_unicode_to_ascii
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import unicodedata


def lossy_unicode_to_ascii(unicode_str):
    """Return a lossy conversion of 'unicode_str' from unicode to ascii.

    This function make a 'best effort' to do the conversion and will not raise
    errors if it does not manage to do a 1-1 mapping.

    Codepoints which could not be converted will be replaced by '?'.

    Usage examples:

        Horizontal ellipses character expands to 3 periods
        >>> lossy_unicode_to_ascii(u'\u2026')
        '...'

        Hyphenation point is replaced by question mark
        >>> lossy_unicode_to_ascii(u'\u2027')
        '?'

    :unicode_str: the unicode string to re-encode as ascii
    :returns: the best effort ascii representation of 'unicode_str'

    """
    # first decompose all the glyphs as much as possible - often multiple
    # characters are combined into a single unicode glyph which could be
    # represented ok by themselves.
    decomposed = unicodedata.normalize('NFKD', unicode_str)

    # next, encode as ascii, replacing all characters that can't be encoded
    # with '?' instead.
    replaced = decomposed.encode('ascii', 'replace')

    return replaced


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
