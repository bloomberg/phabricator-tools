"""Test suite for abdt_landinglog."""
#==============================================================================
#                                   TEST PLAN
#------------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] can prepend to landinglog when the landinglog ref doesn't exist yet
# [ A] can push a new file to 'refs/arcyd/landinglog' without being rejected
# [ A] can push to 'refs/arcyd/landinglog' and get from another clone
#------------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
#==============================================================================

from __future__ import absolute_import

import unittest

import phlsys_fs
import phlsys_git
import phlsys_subprocess

import abdt_landinglog


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_Breathing(self):
        with phlsys_fs.chtmpdir_context():
            fetch_config = str(
                'remote.origin.fetch=+refs/arcyd/landinglog'
                ':refs/arcyd/origin/landinglog')

            run = phlsys_subprocess.run_commands

            run('git init --bare origin')
            run('git clone origin dev --config ' + fetch_config)

            with phlsys_fs.chdir_context('dev'):

                # make an initial commit on the master branch
                run('touch README')
                run('git add README')
                run('git commit README -m initial_commit')
                run('git push origin master')
                run('git checkout -b myfeature')

                # create a new branch with unique content
                with open('README', 'w') as f:
                    f.write('myfeature content')
                run('git add README')
                run('git commit README -m myfeature_content')
                run('git push -u origin myfeature')

            dev = phlsys_git.GitClone('dev')

            # make sure we can prepend a branch to the landinglog when empty
            abdt_landinglog.prepend(dev, '1234', 'myfeature', '4567')
            log = abdt_landinglog.get_log(dev)
            self.assertEqual(1, len(log))
            self.assertEqual(log[0].review_sha1, "1234")
            self.assertEqual(log[0].name, "myfeature")
            self.assertEqual(log[0].landed_sha1, "4567")

            # make sure we can prepend another branch
            abdt_landinglog.prepend(dev, '5678', 'newfeature', '8901')
            log = abdt_landinglog.get_log(dev)
            self.assertEqual(2, len(log))
            self.assertEqual(log[0].review_sha1, "5678")
            self.assertEqual(log[0].name, "newfeature")
            self.assertEqual(log[0].landed_sha1, "8901")
            self.assertEqual(log[1].review_sha1, "1234")
            self.assertEqual(log[1].name, "myfeature")
            self.assertEqual(log[1].landed_sha1, "4567")

            # make a new, independent clone and make sure we get the same log
            abdt_landinglog.push_log(dev, 'origin')
            run('git clone origin dev2 --config ' + fetch_config)
            with phlsys_fs.chdir_context('dev2'):
                run('git fetch')
            dev2 = phlsys_git.GitClone('dev2')
            self.assertListEqual(
                abdt_landinglog.get_log(dev),
                abdt_landinglog.get_log(dev2))

            # prepend the max number of entries and make sure 'newfeature' goes
            # for i in xrange(abdt_landinglog._MAX_LOG_LENGTH):
            #     abdt_landinglog.prepend(dev, '90', 'scrolling')
            # log = abdt_landinglog._get_log_raw(dev)
            # self.assertNotIn(log, 'newfeature')


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
