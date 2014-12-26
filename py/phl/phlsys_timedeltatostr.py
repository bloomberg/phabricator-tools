"""Convert timedeltas to strings."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_timedeltatostr
#
# Public Classes:
#   UnitToSeconds
#
# Public Functions:
#   in_custom_unit
#   in_named_unit
#   in_days
#   in_weeks
#   in_months
#   in_years
#   quantized
#
# Public Assignments:
#   UNIT_TO_SECONDS
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class UnitToSeconds(object):  # XXX: will derive from Enum in Python 3.4+
    year = 60 * 60 * 24 * 365  # XXX: based on average days per year
    month = 60 * 60 * 24 * 30  # XXX: based on average days per month
    week = 60 * 60 * 24 * 7
    day = 60 * 60 * 24
    hour = 60 * 60
    minute = 60
    second = 1


UNIT_TO_SECONDS = {
    "year": UnitToSeconds.year,
    "month": UnitToSeconds.month,
    "week": UnitToSeconds.week,
    "day": UnitToSeconds.day,
    "hour": UnitToSeconds.hour,
    "minute": UnitToSeconds.minute,
    "second": UnitToSeconds.second,
}


def in_custom_unit(td, seconds_per_unit, unit_name):
    """Return a string describing the number of whole 'unit_name' in 'td'.

    'seconds_per_unit' is used as the divisor to determine how many whole units
    are present in 'td'.

    If the number of units is other than 1, an 's' is appended to the name of
    the unit to make it plural.

    Usage examples:

        24 hours in days
        >>> import datetime; in_named_unit(
        ...     datetime.timedelta(seconds=60*60*24), 'day')
        '1 day'

        50 hours in days
        >>> import datetime; in_named_unit(
        ...     datetime.timedelta(seconds=60*60*50), 'day')
        '2 days'

    :td: a datetime.timedelta
    :returns: a string describing the supplied 'td'

    """
    seconds = td.total_seconds()
    units = int(seconds // seconds_per_unit)
    if units != 1:
        unit_name += 's'
    return ' '.join([str(units), unit_name])


def in_named_unit(td, unit_name):
    """Return a string describing the number of whole 'unit_name' in 'td'.

    'unit_name' is assumed to be a name that exists in UNIT_TO_SECONDS.

    Usage examples:

        24 hours in days
        >>> import datetime; in_named_unit(
        ...     datetime.timedelta(seconds=60*60*24), 'day')
        '1 day'

        50 hours in days
        >>> import datetime; in_named_unit(
        ...     datetime.timedelta(seconds=60*60*50), 'day')
        '2 days'

    :td: a datetime.timedelta
    :returns: a string describing the supplied 'td'

    """
    return in_custom_unit(td, UNIT_TO_SECONDS[unit_name], unit_name)


def in_days(td):
    """Return a string describing the number of whole days in 'td'.

    Usage examples:

        24 hours
        >>> import datetime; in_days(datetime.timedelta(seconds=60*60*24))
        '1 day'

        50 hours
        >>> import datetime; in_days(datetime.timedelta(seconds=60*60*50))
        '2 days'

    :td: a datetime.timedelta
    :returns: a string describing the supplied 'td'

    """
    return in_custom_unit(td, UnitToSeconds.day, 'day')


def in_weeks(td):
    """Return a string describing the number of whole weeks in 'td'.

    Usage examples:

        8 days
        >>> import datetime; in_weeks(datetime.timedelta(seconds=60*60*24*8))
        '1 week'

        14 days
        >>> import datetime; in_weeks(datetime.timedelta(seconds=60*60*24*14))
        '2 weeks'

    :td: a datetime.timedelta
    :returns: a string describing the supplied 'td'

    """
    return in_custom_unit(td, UnitToSeconds.week, 'week')


def in_months(td):
    """Return a string describing the number of whole months in 'td'.

    Note that the number of months is approximate, based on the average number
    of days per month.

    Usage examples:

        40 days
        >>> import datetime; in_months(datetime.timedelta(seconds=60*60*24*40))
        '1 month'

        80 days
        >>> import datetime; in_months(datetime.timedelta(seconds=60*60*24*80))
        '2 months'

    :td: a datetime.timedelta
    :returns: a string describing the supplied 'td'

    """
    return in_custom_unit(td, UnitToSeconds.month, 'month')


def in_years(td):
    """Return a string describing the number of whole years in 'td'.

    Note that the number of years is approximate, based on the average number
    of days per year.

    Usage examples:

        365 days
        >>> import datetime; in_years(datetime.timedelta(seconds=60*60*24*365))
        '1 year'

        800 days
        >>> import datetime; in_years(datetime.timedelta(seconds=60*60*24*800))
        '2 years'

    :td: a datetime.timedelta
    :returns: a string describing the supplied 'td'

    """
    return in_custom_unit(td, UnitToSeconds.year, 'year')


def quantized(td):
    """Return a string based on the supplied datetime.timedelta 'td'.

    Generate descriptions that fall nicely into buckets so that timedeltas
    that happened at 'roughly' the same time will have the same description.

    The timedelta will be described using the largest 'human' unit that it has
    more than one of; e.g. '1 hour, 20 minutes, 6 seconds' becomes '1 hour'.

    Usage examples:
        quantize 1 hour, 20 minutes, 6 seconds
        >>> import datetime; quantized(datetime.timedelta(seconds=60*80+6))
        '1 hour'

        quantize 2.1 hours
        >>> import datetime; quantized(datetime.timedelta(seconds=60*60*2.1))
        '2 hours'

        quantize 1 day, 60 seconds
        >>> import datetime; quantized(datetime.timedelta(days=1, seconds=60))
        '1 day'

        quantize 20 seconds
        >>> import datetime; quantized(datetime.timedelta(seconds=20))
        '20 seconds'

        quantize 0 seconds
        >>> import datetime; quantized(datetime.timedelta(seconds=0))
        'no time'

    :td: a datetime.timedelta
    :returns: a string describing the supplied 'td'

    """
    buckets = [
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 7 * 4),
        ("week", 60 * 60 * 24 * 7),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]

    remainder = td.total_seconds()
    for (unit_name, seconds_per_unit) in buckets:
        units = int(remainder // seconds_per_unit)
        if units >= 1:
            if units > 1:
                unit_name += 's'
            return str(units) + " " + unit_name

    return "no time"


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
