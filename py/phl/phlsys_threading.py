"""Helpers for multi-threading."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_threading
#
# Public Classes:
#   MultiResource
#    .resource_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import threading


class MultiResource(object):

    """Allocate and share resources in a thread-safe manner."""

    def __init__(self, max_resources, factory):
        """Create a new MultiResource, use 'factory' to create new resources.

        Will call 'factory' at most 'max_resources' times.
        Note that 'factory' must be thread-safe.

        :max_resources: integer
        :factory: a callable that returns a new resource

        """
        if max_resources < 1:
            raise ValueError(
                'max_resources should be at least 1, got {}'.format(
                    max_resources))
        self._free_resources = []
        self._used_resources = []
        self._condition = threading.Condition()
        self._max_resources = max_resources
        self._factory = factory

    @contextlib.contextmanager
    def resource_context(self):
        with self._condition:
            while not self._free_resources:
                if len(self._used_resources) < self._max_resources:
                    self._free_resources.append(self._factory())
                else:
                    self._condition.wait()
            resource = self._free_resources.pop()
            self._used_resources.append(resource)
        try:
            yield resource
        finally:
            with self._condition:
                self._free_resources.append(resource)
                self._condition.notify()


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
