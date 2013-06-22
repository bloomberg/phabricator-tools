"""Convert timedeltas to strings."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
#
# Public Functions:
#   quantized
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================


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
    remainder = td.total_seconds()
    buckets = [
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 7 * 4),
        ("week", 60 * 60 * 24 * 7),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]

    for (unit_name, seconds_per_unit) in buckets:
        units, remainder = divmod(remainder, seconds_per_unit)
        if units >= 1:
            int_units = int(units)
            if units > 1:
                unit_name += 's'
            return str(int_units) + " " + unit_name

    return "no time"


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
