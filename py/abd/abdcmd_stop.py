"""Stop the arcyd instance for the current directory."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmd_stop
#
# Public Functions:
#   getFromfilePrefixChars
#   setupParser
#   process
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abdi_startstop


def getFromfilePrefixChars():
    return None


def setupParser(parser):
    parser.add_argument(
        '-m',
        '--message',
        default='',
        help="reason for stopping arcyd")


def process(args):
    abdi_startstop.stop_arcyd(args.message)


# -----------------------------------------------------------------------------
# Copyright (C) 2014-2015 Bloomberg Finance L.P.
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
