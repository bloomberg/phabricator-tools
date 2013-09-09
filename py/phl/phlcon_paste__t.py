"""Test suite for phlcon_paste."""

from __future__ import absolute_import

import unittest

import phldef_conduit
import phlsys_conduit

import phlcon_paste

#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [  ] TODO
#------------------------------------------------------------------------------
# Tests:
# TODO
#==============================================================================


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)
        self.conduit = None

    def setUp(self):
        test_data = phldef_conduit
        self.conduit = phlsys_conduit.Conduit(
            test_data.TEST_URI,
            test_data.ALICE.user,
            test_data.ALICE.certificate)

    def tearDown(self):
        pass

    def testCreatePaste(self):
        title = "paste created in tests"
        language = "text"
        content = "blah blah blah this is a paste"

        pasteResponse = phlcon_paste.create_paste(
            self.conduit, content, title, language)

        self.assertEqual(pasteResponse.content, content)
        self.assertEqual(pasteResponse.title, title)
        self.assertEqual(pasteResponse.language, language)

#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
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
#------------------------------- END-OF-FILE ----------------------------------
