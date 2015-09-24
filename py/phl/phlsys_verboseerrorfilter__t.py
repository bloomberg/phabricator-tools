"""Test suite for phlsys_verboseerrorfilter."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] VerboseErrorFilter can be added to log handler
# [ B] Error log contains both - concise and verbose messages
# [ B] info log contains concise message
# [ B] info log does not contains verbose message
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_breathing
# [ B] test_B_verbose_filter
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import logging.handlers
import unittest

import phlsys_fs
import phlsys_verboseerrorfilter

_LOGGER = logging.getLogger(__name__)


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_breathing(self):
        pass

    def test_B_verbose_filter(self):
        # pychecker makes us do this, it won't recognise that logging.handlers
        # is a thing.
        lg = logging
        with phlsys_fs.chtmpdir_context():
            error_handler = lg.handlers.RotatingFileHandler(
                'errorlog',
                maxBytes=10 * 1024,
                backupCount=10)
            error_handler.setLevel(logging.ERROR)
            logging.getLogger().addHandler(error_handler)

            info_handler = lg.handlers.RotatingFileHandler(
                'infolog',
                maxBytes=10 * 1024,
                backupCount=10)
            info_handler.setLevel(logging.INFO)
            # [ B] VerboseErrorFilter can be added to log handler
            info_handler.addFilter(phlsys_verboseerrorfilter.getFilter())
            logging.getLogger().addHandler(info_handler)

            concise_message = "This is a concise error message."
            verbose_message = "VERBOSE MESSAGE: This is a verbose error "
            "message. This should not appear in error log but not in info log."
            _LOGGER.error(concise_message)
            _LOGGER.error(verbose_message)

            with open('errorlog') as f:
                # [ B] Error log contains both - concise and verbose messages
                error_log = f.read()
                self.assertTrue(concise_message in error_log)
                self.assertTrue(verbose_message in error_log)

            with open('infolog') as f:
                info_log = f.read()
                # [ B] info log contains concise message
                self.assertTrue(concise_message in info_log)
                # [ B] info log does not contains verbose message
                self.assertFalse(verbose_message in info_log)

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
