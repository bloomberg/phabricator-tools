"""Provide equivalent classes that write dictionaries to shared resources."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_shareddictoutput
#
# Public Classes:
#   ToFile
#    .write
#   ToDict
#    .write
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import json
import os

import phlsys_fs


class ToFile(object):

    def __init__(self, filename):
        super(ToFile, self).__init__()
        self._filename = os.path.abspath(filename)

    def write(self, d):
        assert isinstance(d, dict)
        with phlsys_fs.write_file_lock_context(self._filename) as f:
            f.write(json.dumps(d))


class ToDict(object):

    def __init__(self, shared_d):
        super(ToDict, self).__init__()
        self._shared_d = shared_d
        assert isinstance(self._shared_d, dict)

    def write(self, d):
        assert isinstance(d, dict)
        # copy contents to other dict
        self._shared_d.clear()
        self._shared_d.update(d)


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
