"""Tools for managing a web server."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_web
#
# Public Classes:
#   SimpleWebServer
#    .close
#
# Public Functions:
#   pick_free_port
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import socket
import subprocess

import phlsys_pid


def pick_free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class SimpleWebServer(object):

    def __init__(self, root_path, port):
        self._root_path = root_path
        self._process = subprocess.Popen(
            ['python', '-m', 'SimpleHTTPServer', str(port)],
            cwd=root_path)

    def close(self):
        pid = self._process.pid
        phlsys_pid.request_terminate(pid)
        self._process.wait()
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
