"""Filter for log handlers to exclude verbose error messages."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_verboseerrorfilter
#
# Public Classes:
#   VerboseErrorFilter
#    .filter
#
# Public Functions:
#   make_filter
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging


class VerboseErrorFilter(logging.Filter):

    def filter(self, record):
        if record.levelno == logging.ERROR and \
           record.getMessage().startswith("VERBOSE MESSAGE"):
            return False
        else:
            return True


def make_filter():
    return VerboseErrorFilter()

# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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
