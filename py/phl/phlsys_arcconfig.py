"""Wrapper to integrate with Arcanist's .arcconfig file."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_arcconfig
#
# Public Functions:
#   find_arcconfig
#   load
#   get_arcconfig
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os


def _parent_dir(path):
    return os.path.abspath(os.path.join(path, os.pardir))


def find_arcconfig():
    path = None
    nextpath = os.getcwd()
    while path != nextpath:
        path, nextpath = nextpath, _parent_dir(nextpath)
        config_path = os.path.join(path, ".arcconfig")
        if os.path.isfile(config_path):
            return config_path
    return None


def load(path):
    with open(path) as f:
        return json.load(f)


def get_arcconfig():
    return load(find_arcconfig())


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
