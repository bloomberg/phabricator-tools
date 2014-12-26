"""Wrapper to call git, with working directory."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_git
#
# Public Classes:
#   Repo
#    .working_dir
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import phlsys_subprocess


class Repo(object):

    def __init__(self, workingDir):
        self._workingDir = os.path.abspath(workingDir)

    # def __call__(*args, stdin=None): <-- supported in Python 3
    def __call__(self, *args, **kwargs):
        stdin = kwargs.pop("stdin", None)
        assert(not kwargs)
        result = phlsys_subprocess.run(
            'git', *args,
            stdin=stdin, workingDir=self._workingDir)
        return result.stdout

    @property
    def working_dir(self):
        return self._workingDir


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
