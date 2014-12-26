"""Test suite for abdt_naming."""
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
from __future__ import division
from __future__ import print_function

import unittest

# import abdt_naming


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        # Usage example:
        #     >>> naming = ClassicNaming()
        #     >>> func = naming.make_tracker_branch_from_name
        #     >>> _get_branches(['dev/arcyd/ok/mywork/master/99'], func)
        # ... # doctest: +NORMALIZE_WHITESPACE
        #     [abdt_naming.TrackerBranch("dev/arcyd/ok/mywork/master/99")]
        #
        #     >>> _get_branches([], func)
        #     []
        #
        #     >>> _get_branches(['invalid'], func)
        #     []
        #
        pass


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
