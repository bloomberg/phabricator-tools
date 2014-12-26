"""A simple wrapper to call sendmail-like binary."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_sendmail
#
# Public Classes:
#   Sendmail
#    .set_default_binary
#    .set_default_params_from_type
#    .send
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import phlsys_subprocess


class Sendmail():

    _default_binary = 'sendmail'
    _default_params = ['-t']

    @classmethod
    def set_default_binary(cls, binary):
        cls._default_binary = binary

    @classmethod
    def set_default_params_from_type(cls, sendmail_type):
        if "sendmail" == sendmail_type:
            cls._default_params = ["-t"]
        elif "catchmail" == sendmail_type:
            cls._default_params = []
        else:
            raise TypeError(str(sendmail_type) + " is not a type of sendmail")

    def __init__(self, binary=None, params=None):
        """Simply copy the supplied parameters and store in the object.

        :binary: the binary to execute, 'sendmail' if None

        Note that other binaries that are sendmail-compatabile, like
        'catchmail' can be used here instead.

        """
        self._binary = binary if binary is not None else self._default_binary
        self._params = params if params is not None else self._default_params

    # def call(*args, stdin=None): <-- supported in Python 3
    def send(self, stdin):
        result = phlsys_subprocess.run(
            self._binary, *self._params, stdin=stdin)
        return result.stdout


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
