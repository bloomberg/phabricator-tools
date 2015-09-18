"""Test suite for phlsys_compressedlogging."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] CompressedRotatingFileHandler can be initialzed
# [ A] log file is created after initialization
# [ A] the debug handler can be added to logger
# [ A] no extra files are created by the debug handler
# [ B] current log can be rotated to compressed one
# [ B] current log is deleted after rotation
# [ C] number of compressed files do not exceed backupCount
# [ C] existing files are rotated correctly
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_filehandler_breathing
# [ B] test_B_rotation
# [ C] test_C_existing_files_rotation
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import gzip
import logging
import os
import unittest

import phlsys_compressedlogging
import phlsys_fs

_LOGGER = logging.getLogger(__name__)
_MAKE_HANDLER = phlsys_compressedlogging.CompressedRotatingFileHandler


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_filehandler_breathing(self):
        with phlsys_fs.chtmpdir_context():
            # [ A] CompressedRotatingFileHandler can be initialzed
            debug_handler = _MAKE_HANDLER(
                'testfile',
                maxBytes=10 * 1024,
                backupCount=2)
            debug_handler.setLevel(logging.DEBUG)

            # [ A] log file is created after initialization
            self.assertTrue(os.path.exists('testfile'))
            # [ A] the debug handler can be added to logger
            logging.getLogger().addHandler(debug_handler)

            for _ in xrange(1000):
                _LOGGER.debug('Hello World, this is conetent for debug log.')

            # [ A] no extra files are created by the debug handler
            expected_files = ['testfile', 'testfile.1.gz', 'testfile.2.gz']
            self.assertItemsEqual(expected_files, os.listdir('.'))

    def test_B_rotation(self):
        with phlsys_fs.chtmpdir_context():
            debug_handler = _MAKE_HANDLER(
                'testfile')
            content = 'Hello World, this is a test for the rotator.'

            phlsys_fs.write_text_file('testfile', content)
            debug_handler.rotator('testfile', 'dest.gz')

            with gzip.open('dest.gz', 'rb') as dest:
                # [ B] current log can be rotated to compressed one
                self.assertEqual(content, dest.read())
            # [ B] current log is deleted after rotation
            self.assertFalse(os.path.exists('testfile'))

    def test_C_existing_files_rotation(self):
        with phlsys_fs.chtmpdir_context():
            debug_handler = _MAKE_HANDLER(
                'testfile',
                backupCount=2)
            content1 = 'Hello World, this is conetent for testfile1.'
            content2 = 'Hello World, this is conetent for testfile2.'

            with gzip.open('testfile.1.gz', 'wb') as f:
                f.write(content1)
            with gzip.open('testfile.2.gz', 'wb') as f:
                f.write(content2)
            debug_handler.rotate_existing_files()

            # [ C] number of compressed files do not exceed backupCount
            self.assertFalse(os.path.exists('testfile.3.gz'))

            # [ C] existing files are rotated correctly
            self.assertFalse(os.path.exists('testfile.1.gz'))
            with gzip.open('testfile.2.gz', 'rb') as f:
                self.assertEqual(content1, f.read())


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
