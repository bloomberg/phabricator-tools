"""Test suite for phlsys_cppceck."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [  ]
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# =============================================================================

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
