"""A poor substitute for PHP's strtotime function."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_strtotime
#
# Public Functions:
#   describe_duration_string_to_time_delta
#   duration_string_to_time_delta
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import datetime


def describe_duration_string_to_time_delta():
    return str('time can be specified like "5 hours 20 minutes", use '
               'combinations of seconds, minutes, hours, days, weeks. '
               'each unit should only appear once.  you may use floating '
               'point numbers and negative numbers. '
               'e.g. "1 weeks -1.5 days".')


def duration_string_to_time_delta(s):
    """Return a datetime.timedelta based on the supplied string 's'.

    Usage examples:
        >>> str(duration_string_to_time_delta("1 seconds"))
        '0:00:01'

        >>> str(duration_string_to_time_delta("2 minutes"))
        '0:02:00'

        >>> str(duration_string_to_time_delta("2 hours 2 minutes"))
        '2:02:00'

        >>> str(duration_string_to_time_delta("1 days 2 hours 2 minutes"))
        '1 day, 2:02:00'

        >>> str(duration_string_to_time_delta("1.5 days"))
        '1 day, 12:00:00'

        >>> str(duration_string_to_time_delta("1 days -1 hours"))
        '23:00:00'

        >>> str(duration_string_to_time_delta("1 milliseconds"))
        '0:00:00.001000'

    :s: a string in the appropriate time format
    :returns: a datetime.timedelta

    """
    clauses = s.split()
    if len(clauses) % 2:
        raise ValueError("odd number of clauses: " + s)
    pairs = zip(clauses[::2], clauses[1::2])
    d = {p[1]: float(p[0]) for p in pairs}
    if len(d) != len(pairs):
        raise ValueError("duplicated clauses: " + s)
    return datetime.timedelta(**d)


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
