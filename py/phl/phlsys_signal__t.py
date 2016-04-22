"""Test suite for phlsys_signal."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] can run phlsys_signal.set_exit_on_sigterm
# [ A] exit_level is 0 before exit contexts are active
# [ A] exit_level is 1 while single exit context is active
# [ A] exit_level is 0 after single exit contexts finishes
# [ B] exit_level is 0 before recursive exit contexts are active
# [ B] exit_level is 1 while first exit context is active
# [ B] exit_level is 2 while second exit context is active
# [ B] exit_level is 0 after recursive exit contexts are active
# [ C] exceptions can be raised through an exit context
# [ C] exit_level is 0 after raising through an exit context
# [ D] exceptions cannot be raised through a triggered exit context
# [ D] exit_level is 0 after raising through triggered exit context
# [ E] cannot raise through nested triggered exit contexts
# [ E] exit_level=0 after raising through nested triggered contexts
# [ F] After SIGTERM is received, exit contexts raise SystemExit
# [ F] exit_level is 0 after a triggered exit context
# [ G] When nesting exit contexts, exit after SIGTERM is received
# [ G] When nesting exit contexts, finish after SIGTERM is received
# [ G] exit_level is 0 after triggered nested exit contexts finish
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# [ B] test_B_can_recurse_exit_context
# [ C] test_C_can_raise_through_exit_context
# [ D] test_D_cant_raise_through_triggered_exit_context
# [ E] test_E_cant_raise_through_nested_triggered_exit_context
# [ F] test_F_after_sigterm_exit_contexts_do_exit
# [ G] test_G_after_sigterm_inner_exit_contexts_do_not_exit
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import phlsys_signal


class Test(unittest.TestCase):

    def __init__(self, data):
        super(Test, self).__init__(data)

    def test_A_Breathing(self):
        # CONCERN: can run phlsys_signal.set_exit_on_sigterm
        phlsys_signal.set_exit_on_sigterm()

        # CONCERN: exit_level is 0 before exit contexts are active
        self.assertEqual(
            phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
            0)
        with phlsys_signal.no_exit_context():
            # CONCERN: exit_level is 1 while single exit context is active
            self.assertEqual(
                phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
                1)
        # CONCERN: exit_level is 0 after single exit contexts finishes
        self.assertEqual(
            phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
            0)

    def test_B_can_recurse_exit_context(self):
        # CONCERN: exit_level is 0 before recursive exit contexts are active
        self.assertEqual(
            phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
            0)
        with phlsys_signal.no_exit_context():
            # CONCERN: exit_level is 1 while first exit context is active
            self.assertEqual(
                phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
                1)
            with phlsys_signal.no_exit_context():
                # CONCERN: exit_level is 2 while second exit context is active
                self.assertEqual(
                    phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
                    2)
        # CONCERN: exit_level is 0 after recursive exit contexts are active
        self.assertEqual(
            phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
            0)

    def test_C_can_raise_through_exit_context(self):
        class RaiseThroughExitError(Exception):
            pass

        # CONCERN: exceptions can be raised through an exit context
        with self.assertRaises(RaiseThroughExitError):
            with phlsys_signal.no_exit_context():
                raise RaiseThroughExitError()

        # CONCERN: exit_level is 0 after raising through an exit context
        self.assertEqual(
            phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
            0)

    def test_D_cant_raise_through_triggered_exit_context(self):
        class RaiseThroughExitError(Exception):
            pass

        # CONCERN: exceptions cannot be raised through a triggered exit context
        with self.assertRaises(SystemExit):
            with phlsys_signal.no_exit_context():
                phlsys_signal._SIGNAL_FLAGS.got_sigterm = True
                raise RaiseThroughExitError()

        # CONCERN: exit_level is 0 after raising through triggered exit context
        self.assertEqual(
            phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
            0)

    def test_E_cant_raise_through_nested_triggered_exit_context(self):
        class RaiseThroughExitError(Exception):
            pass

        # CONCERN: cannot raise through nested triggered exit contexts
        with self.assertRaises(SystemExit):
            with phlsys_signal.no_exit_context():
                with phlsys_signal.no_exit_context():
                    phlsys_signal._SIGNAL_FLAGS.got_sigterm = True
                    raise RaiseThroughExitError()

        # CONCERN: exit_level=0 after raising through nested triggered contexts
        self.assertEqual(
            phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
            0)

    def test_F_after_sigterm_exit_contexts_do_exit(self):
        # CONCERN: After SIGTERM is received, exit contexts raise SystemExit
        with self.assertRaises(SystemExit):
            with phlsys_signal.no_exit_context():
                phlsys_signal._SIGNAL_FLAGS.got_sigterm = True

        # CONCERN: exit_level is 0 after a triggered exit context
        self.assertEqual(
            phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
            0)

    def test_G_after_sigterm_inner_exit_contexts_do_not_exit(self):
        did_finish = False

        # CONCERN: When nesting exit contexts, exit after SIGTERM is received
        with self.assertRaises(SystemExit):
            with phlsys_signal.no_exit_context():
                with phlsys_signal.no_exit_context():
                    with phlsys_signal.no_exit_context():
                        phlsys_signal._SIGNAL_FLAGS.got_sigterm = True
                did_finish = True

        # CONCERN: When nesting exit contexts, finish after SIGTERM is received
        self.assertTrue(did_finish)

        # CONCERN: exit_level is 0 after triggered nested exit contexts finish
        self.assertEqual(
            phlsys_signal._SIGNAL_FLAGS.delay_sigterm_exit_level,
            0)


# -----------------------------------------------------------------------------
# Copyright (C) 2016 Bloomberg Finance L.P.
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
