"""Test suite for abdt_landinglog."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] can prepend to landinglog when the landinglog ref doesn't exist yet
# [ A] can push a new file to 'refs/arcyd/landinglog' without being rejected
# [ A] can push to 'refs/arcyd/landinglog' and get from another clone
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_Breathing
# =============================================================================

from __future__ import print_function
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

            dev = phlsys_git.Repo('dev')

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
            dev2 = phlsys_git.Repo('dev2')
            self.assertListEqual(
                abdt_landinglog.get_log(dev),
                abdt_landinglog.get_log(dev2))

            # prepend the max number of entries and make sure 'newfeature' goes
            # for i in xrange(abdt_landinglog._MAX_LOG_LENGTH):
            #     abdt_landinglog.prepend(dev, '90', 'scrolling')
            # log = abdt_landinglog._get_log_raw(dev)
            # self.assertNotIn(log, 'newfeature')


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
