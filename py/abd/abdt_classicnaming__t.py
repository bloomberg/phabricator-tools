"""Test suite for abdt_classicnaming."""
#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [  ]
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
#==============================================================================

from __future__ import absolute_import

import unittest

import abdt_classicnaming
import abdt_naming


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        naming = abdt_classicnaming.Naming()

        b = "invalidreviewname"
        self.assertRaises(
            abdt_naming.Error, lambda: naming.make_review_branch_from_name(b))
        self.assertRaises(
            abdt_naming.Error, lambda: naming.make_tracker_branch_from_name(b))

        b = "arcyd-review/"
        self.assertRaises(
            abdt_naming.Error, lambda: naming.make_review_branch_from_name(b))
        self.assertRaises(
            abdt_naming.Error, lambda: naming.make_tracker_branch_from_name(b))

        b = naming.make_review_branch_name("mywork", "master")
        r = naming.make_review_branch_from_name(b)
        self.assertTrue(r)
        self.assertEqual(r.branch, b)
        self.assertEqual(r.description, "mywork")
        self.assertEqual(r.base, "master")
        self.assertRaises(
            abdt_naming.Error, lambda: naming.make_tracker_branch_from_name(b))

        b = naming.make_tracker_branch_name("ok", "mywork", "master", 1)
        self.assertRaises(
            abdt_naming.Error, lambda: naming.make_review_branch_from_name(b))
        w = naming.make_tracker_branch_from_name(b)
        self.assertTrue(w)
        self.assertEqual(w.branch, b)
        self.assertEqual(w.status, "ok")
        self.assertEqual(w.description, "mywork")
        self.assertEqual(w.base, "master")
        self.assertEqual(w.id, "1")


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
