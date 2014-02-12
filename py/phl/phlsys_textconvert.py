"""Convert between unicode and ascii easily."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_textconvert
#
# Public Functions:
#   lossy_unicode_to_ascii
#   to_unicode
#
# Public Assignments:
#   UNICODE_REPLACEMENTS
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import unicodedata

# Unicode characters with sensible ASCII equivalents
UNICODE_REPLACEMENTS = {
    u"\u2010": u"-",    # Hyphen
    u"\u2011": u"-",    # Non-breaking hyphen
    u"\u2013": u"-",    # Figure dash
    u"\u2013": u"-",    # En-dash
    u"\u2014": u"-",    # Em-dash
    u"\u2015": u"-",    # Horizontal bar
    u"\u2212": u"-",    # Minus sign

    u"\u00b4": u"'",    # Acute accent
    u"\u2018": u"'",    # Left single quote
    u"\u2019": u"'",    # Right single quote
    u"\u201c": u'"',    # Left double quote
    u"\u201d": u'"',    # Right double quote

    u"\u00b7": u"*",    # Middle dot
    u"\u2022": u"*",    # Bullet
    u"\u2023": u">",    # Triangular bullet
    u"\u2024": u"*",    # One dot leader
    u"\u2043": u"-",    # Hyphen bullet
    u"\u25b8": u">",    # Black right-pointing small triangle
    u"\u25e6": u"o",    # White bullet
}


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
    # first, apply a set of pre-defined substitutions to preserve common cases
    # like em-dashes and smart quotes.
    substituted = unicode_str
    for src, dst in UNICODE_REPLACEMENTS.iteritems():
        substituted = substituted.replace(src, dst)

    # next, decompose all the glyphs as much as possible - often multiple
    # characters are combined into a single unicode glyph which could be
    # represented ok by themselves.
    decomposed = unicodedata.normalize('NFKD', substituted)

    # finally, encode as ascii, replacing all characters that can't be encoded
    # with '?' instead.
    replaced = decomposed.encode('ascii', 'replace')

    return replaced


def to_unicode(s, errors=None):
    """Return a unicode string from the supplied string 's'.

    If there are invalid characters in the string 's' then they will be
    replaced with the unicode replacement character (U+FFFD).

    The error behavior can be overriden by supplying a string value for error
    of ('strict', 'replace' or 'ignore) which behave identically to the builtin
    unicode.

    If 's' is already a unicode string then no action will be taken

    """
    if errors is None:
        errors = 'replace'

    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        return unicode(s, errors=errors)
    else:
        raise TypeError('not a str or unicode')


#------------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
