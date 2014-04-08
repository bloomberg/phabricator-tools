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
# ------------------------------ END-OF-FILE ----------------------------------
