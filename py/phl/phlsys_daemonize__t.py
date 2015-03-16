"""Test suite for phlsys_daemonize."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import unittest

import phlsys_daemonize

# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ B] parent standard IO descriptors are released
# [ C] daemonize controlling process doesn't die of SIGHUP
# -----------------------------------------------------------------------------
# Tests:
# [BC] test_A_Stdio
# =============================================================================


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        pass

    def test_B_Stdio(self):
        # lookup file descriptors for original stdio objects
        stdio_fo = [sys.__stdin__, sys.__stdout__, sys.__stderr__]
        stdio_fd = [f.fileno() for f in stdio_fo]

        # create subprocess to deamonize. pipe will be used to communicate
        # back information about daemonized process
        pipe_r, pipe_w = os.pipe()

        # forkpty is used to make situation more tricky for phlsys_daemonize:
        # the child process will be a controlling process which makes its
        # children potential targets of SIGHUP on its exit
        child_pid, child_pty = os.forkpty()

        if child_pid == 0:
            os.close(pipe_r)

            phlsys_daemonize.do()

            pipe_wf = os.fdopen(pipe_w, 'w')
            try:
                # report that process survived the daemonization
                pipe_wf.write('daemonized\n')

                # dump file names of files opened as stdin, stdout and stderr
                proc_dir = '/proc/%i/' % os.getpid()
                for fd in stdio_fd:
                    proc_entry = 'fd/%i' % fd
                    target = os.readlink(proc_dir + proc_entry)
                    pipe_wf.write(proc_entry + ' => ' + target + '\n')

            except Exception, e:
                pipe_wf.write(str(e))

            sys.exit(0)

        os.close(pipe_w)
        pipe_rf = os.fdopen(pipe_r, 'r')

        ret_pid, ret_err = os.waitpid(child_pid, 0)

        self.assertEqual(ret_pid, child_pid)
        self.assertEqual(ret_err, 0)

        expected_fd_links = ['fd/%i => /dev/null' % fd for fd in stdio_fd]
        expected_output = ['daemonized'] + expected_fd_links

        daemon_output = [line.strip() for line in pipe_rf.readlines()]

        self.assertEqual(daemon_output, expected_output)


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
