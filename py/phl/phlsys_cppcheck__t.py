"""Test suite for phlsys_cppceck."""
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

import phlsys_cppcheck


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        output = """\
<?xml version="1.0" encoding="UTF-8"?>
<results version="2">
  <cppcheck version="1.58"/>
  <errors>
  <error id="nullPointer" severity="error" msg="Possible null pointer \
dereference: s - otherwise it is redundant to check it against null." \
verbose="Possible null pointer dereference: s - otherwise it is redundant \
to check it against null.">
    <location file="hello_world_bad.cpp" line="11"/>
    <location file="hello_world_bad.cpp" line="10"/>
  </error>
  <error id="nullPointer" severity="error" msg="Null pointer dereference" \
verbose="Null pointer dereference">
    <location file="hello_world_bad.cpp" line="7"/>
  </error>
  </errors>
</results>"""

        expected = [
            ('error', 'nullPointer', 'hello_world_bad.cpp', [11, 10],
                'Possible null pointer dereference: s - otherwise it is '
                'redundant to check it against null.'),
            ('error', 'nullPointer', 'hello_world_bad.cpp', [7],
                'Null pointer dereference'),
        ]

        expected = [phlsys_cppcheck.Result(*x) for x in expected]

        self.assertEqual(
            phlsys_cppcheck.parse_output(output),
            expected)

        self.assertIsInstance(
            phlsys_cppcheck.summarize_results(expected),
            str)


#------------------------------------------------------------------------------
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
#------------------------------- END-OF-FILE ----------------------------------
