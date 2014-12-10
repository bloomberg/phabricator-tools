"""Helpers for multi-processing."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlsys_multiprocessing
#
# Public Classes:
#   MultiResource
#    .resource_context
#
# Public Functions:
#   logging_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import logging
import multiprocessing
import multiprocessing.queues


@contextlib.contextmanager
def logging_context(logging_configurer_fn, logging_level=logging.DEBUG):
    """A context manager that creates a separate process for logging.

    Sets up the current process to log via a multiprocessing queue to the
    logging process.

    Note that after the scope of the context, logging will cease to function as
    it will be queuing log entries for the expired logging process.

    :logging_configurer_fn: a callable to configure logging process
    :logging_level: optional logging level, defaults to logging.DEBUG

    """
    logging_queue = multiprocessing.Queue()
    logging_process_object = multiprocessing.Process(
        target=_logging_process,
        args=(logging_queue, logging_configurer_fn))
    logging_process_object.start()

    # configure the current process to log to the logger process
    handler = _QueueLoggingHandler(logging_queue)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging_level)

    try:
        yield
    finally:
        # instruct the logger process to stop by sending it 'None'
        logging_queue.put_nowait(None)
        logging_process_object.join()


def _logging_process(logging_queue, logging_configurer_fn):

    logging_configurer_fn()

    while True:
        record = logging_queue.get()

        # we will receive 'None' if we are to stop processing
        if record is None:
            break

        # dispatch to the appropriate logger, so that any individual
        # module customizations work as expected
        logger = logging.getLogger(record.name)
        logger.handle(record)


# in Python 3.2+ there is 'logging.QueueHandler' which does the same job
class _QueueLoggingHandler(logging.Handler):

    def __init__(self, logging_queue):
        super(_QueueLoggingHandler, self).__init__()
        self._logging_queue = logging_queue

    def _prepare(self, record):
        # Arguments and exceptions could cause us trouble when pickling them to
        # send over to the logging process. Bake them into the message string
        # instead of sending them as objects.

        if record.args:
            # note that this could raise, so should be caught by callers
            record.msg = record.msg % record.args

        if record.exc_info:
            # do a premature and unconfigured 'format' if we encounter an
            # exception, so that it won't need to be pickled over to the
            # logging process
            self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            self._logging_queue.put_nowait(
                self._prepare(record))
        except:
            self.handleError(record)


class _NotAResource(object):
    pass


class MultiResource(object):

    """Allocate and share resources in a multiprocess-safe manner."""

    def __init__(self, max_resources, factory):
        """Create a new MultiResource, use 'factory' to create new resources.

        Will call 'factory' at most 'max_resources' times.
        Note that 'factory' must be multiprocess-safe.

        :max_resources: integer
        :factory: a callable that returns a new resource

        """
        if max_resources < 1:
            raise ValueError(
                'max_resources should be at least 1, got {}'.format(
                    max_resources))
        self._factory = factory

        # pychecker makes us do this, it won't recognise that
        # multiprocessing.queues is a thing.
        mp = multiprocessing
        self._free_resources = mp.queues.SimpleQueue()
        for _ in xrange(max_resources):
            self._free_resources.put(_NotAResource)

    @contextlib.contextmanager
    def resource_context(self):
        resource = self._free_resources.get()
        if resource is _NotAResource:
            resource = self._factory()

        try:
            yield resource
        finally:
            self._free_resources.put(resource)


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
