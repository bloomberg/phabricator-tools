"""Test suite for phlsys_multiprocessing."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# TODO
# -----------------------------------------------------------------------------
# Tests:
# TODO
# =============================================================================

from __future__ import absolute_import

import logging
import multiprocessing
import unittest

import phlsys_multiprocessing


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_logging_context_breathing(self):

        def logger_config():
            logging.basicConfig()

        with phlsys_multiprocessing.logging_context(logger_config):
            logging.debug("logging test")

    def test_multiresource_breathing(self):

        def factory():
            return "resource"

        # make sure that we can get a resource in the main process
        multi_resource = phlsys_multiprocessing.MultiResource(1, factory)
        with multi_resource.resource_context() as resource:
            self.assertEqual("resource", resource)
        with multi_resource.resource_context() as resource:
            self.assertEqual("resource", resource)

    def test_multiresource_changes_propagate(self):

        def worker(resource):
            with resource.resource_context() as r:
                r.append("worker process")

        def factory():
            return ["main process"]

        multi_resource = phlsys_multiprocessing.MultiResource(1, factory)

        worker_list = []
        num_workers = 5
        for _ in xrange(num_workers):
            worker_list.append(
                multiprocessing.Process(target=worker, args=(multi_resource,)))
            worker_list[-1].start()
        for w in worker_list:
            w.join()
        with multi_resource.resource_context() as r:
            self.assertEqual(len(r), num_workers + 1)


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
