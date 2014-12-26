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
from __future__ import division
from __future__ import print_function

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
