"""Wrapper to integrate with Arcanist's ~/.arcrc file."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_arcrc
#
# Public Functions:
#   find_arcrc
#   load
#   get_arcrc
#   get_host
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import json
import os.path

import phlsys_conduit


def find_arcrc():
    home = os.path.expanduser("~")
    path = os.path.join(home, ".arcrc")
    if os.path.isfile(path):
        return path
    return None


def load(path):
    with open(path) as f:
        return json.load(f)


def get_arcrc():
    return load(find_arcrc())


def get_host(arcrc, host):
    normalised = phlsys_conduit.make_conduit_uri(host)
    return arcrc["hosts"].get(normalised, None)


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
