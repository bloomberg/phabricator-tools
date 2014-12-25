"""Helpers for process signals."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_signal
#
# Public Functions:
#   set_exit_on_sigterm
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import print_function

import signal
import sys


def set_exit_on_sigterm():
    def HandleSigterm(unused1, unused2):
        # raises 'SystemExit' exception, which will allow us to clean up
        sys.exit(1)
    signal.signal(signal.SIGTERM, HandleSigterm)


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
