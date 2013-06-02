"""Test suite for abdt_conduit"""

import unittest

import phlcon_differential
import phldef_conduit
import phlsys_conduit

import abdt_conduit


class Test(unittest.TestCase):
    def __init__(self, data):
        super(Test, self).__init__(data)
        self.test_data = None
        self.conduit = None

    def setUp(self):
        self.test_data = phldef_conduit
        self.conduit = phlsys_conduit.Conduit(
            self.test_data.test_uri,
            self.test_data.phab.user,
            self.test_data.phab.certificate)

    def testCreateEmptyRevision(self):
        revision_id = abdt_conduit.createEmptyRevision(
            self.conduit, self.test_data.alice.user)

        revision_list = phlcon_differential.query(self.conduit, [revision_id])
        self.assertEqual(len(revision_list), 1)

    # XXX: re-instate when we have support for reviewers and ccs
    # def testCreateEmptyRevisionReviewersCcs(self):
    #     id = abdt_conduit.createEmptyRevision(
    #         self.conduit,
    #         self.test_data.alice.user,
    #         [self.test_data.bob.user],
    #         [self.test_data.phab.user])
    #     revision_list = phlcon_differential.query(self.conduit, [id])
    #     self.assertEqual(len(revision_list), 1)


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
