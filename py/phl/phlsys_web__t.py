"""Test suite for phlsys_web."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] Ensure pick_free_port returns an available port by trying to bind a
#      socket on that port
# [ B] SimpleWebServer starts without any error
# [ B] SimpleWebServer serves correct content
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_pick_free_port
# [ B] test_B_webserver
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import socket
import tempfile
import time
import unittest
import urllib2

import phlsys_fs
import phlsys_web


class Test(unittest.TestCase):

    def test_A_pick_free_port(self):
        port = phlsys_web.pick_free_port()
        sock = socket.socket()
        # [ A] Ensure pick_free_port returns an available port by trying to
        #      bind a socket on that port
        sock.bind(('', port))
        sock.close()

    def test_B_webserver(self):
        port = phlsys_web.pick_free_port()
        dirpath = tempfile.mkdtemp()
        filepath = os.path.join(dirpath, 'index.html')
        phlsys_fs.write_text_file(filepath, 'Hello World')
        # [ B] SimpleWebServer starts without any error
        server = phlsys_web.SimpleWebServer(dirpath, port)
        # Give subprocess enough time to start the server
        time.sleep(1)
        response = urllib2.urlopen("http://localhost:{}".format(port))
        # [ B] SimpleWebServer serves correct content
        self.assertEqual('Hello World', response.read())

        server.close()


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
