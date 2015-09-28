"""phab-ping  - a Phabricator conduit.ping wrapper.

This tool is for checking that Phabricator instances are running as expected.

In the event of an error when communicating with Phabricator, we return -1.
In the event bad arguments we return -2.

For benchmarking Phabricator you might want to take a look at 'Apache Bench'.

"""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# pigcmd_phabping
#
# Public Functions:
#   main
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import collections
import itertools
import sys
import time

import phlsys_conduit

_USAGE_EXAMPLES = """
usage examples:
    ping the official Phabricator install once:
    $ phab-ping https://secure.phabricator.com -c 1

    ping the local Phabricator install indefinitely:
    $ phab-ping http://127.0.0.1
"""


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=_USAGE_EXAMPLES)

    parser.add_argument(
        'destination',
        metavar="destination",
        type=str,
        help="address of the Phabricator instance, e.g. "
        "https://secure.phabricator.com")

    parser.add_argument(
        '--count', '-c',
        metavar="TIMES",
        type=int,
        help="number of times to ping, default is unlimited")

    parser.add_argument(
        '--interval', '-i',
        metavar="SECONDS",
        type=float,
        default=1.0,
        help="wait interval seconds between sending each request, default is "
             "to wait one second. Minimum wait is 0.2 seconds.")

    args = parser.parse_args()

    if args.interval < 0.2:
        print("interval must be at least 0.2 seconds")
        sys.exit(2)

    # perform the ping and display the time taken and result
    uri = phlsys_conduit.make_conduit_uri(args.destination)
    print("conduit.ping " + str(uri))

    if args.count is not None:
        # pychecker requires sequence to be of same type so we have to wrap
        # xrange() in iter() to make it an iterator.
        sequence = iter(xrange(args.count))
    else:
        sequence = itertools.count()

    is_first = True

    Stats = collections.namedtuple(
        "phabping__Stats", ['min', 'max', 'sum', 'count'])
    stats = None

    try:
        for i in sequence:
            # pause between requests
            if not is_first:
                time.sleep(args.interval)

            print("request " + str(i + 1) + " :", end=' ')

            conduit = phlsys_conduit.Conduit(uri)
            start = time.time()
            result = conduit.ping()
            end = time.time()

            msecs = (end - start) * 1000
            print(result, ":", str(int(msecs)), "ms")

            # atomically update the 'stats' object
            # (we may receive KeyboardInterrupt during update)
            if stats is None:
                stats = Stats(min=msecs, max=msecs, sum=msecs, count=i + 1)
            else:
                stats = Stats(
                    min=min(stats.min, msecs),
                    max=max(stats.max, msecs),
                    sum=stats.sum + msecs,
                    count=i + 1)

            is_first = False
    except KeyboardInterrupt:
        # print a newline to separate the ^C
        print()

    if not stats:
        print("no requests processed.")
    else:
        print("---", uri, "conduit.ping statistics", "---")
        print(stats.count, "requests processed")
        print("min / mean / max =", end=' ')
        mean = stats.sum / stats.count
        vals = [stats.min, mean, stats.max]
        vals_str = ' / '.join(["{0:0.2f}".format(i) for i in vals])
        print(vals_str, 'ms')


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
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
