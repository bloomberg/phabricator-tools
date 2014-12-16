"""Log important events appropriately from anywhere in Arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_logging
#
# Public Functions:
#   set_external_system_error_logger
#   clear_external_system_error_logger
#   set_remote_io_write_log_path
#   set_remote_io_read_log_path
#   on_system_error
#   on_retry_exception
#   remote_io_write_event_context
#   remote_io_read_event_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import datetime
import logging
import multiprocessing
import os

import phlsys_subprocess
import phlsys_timer


_LOGGER = logging.getLogger(__name__)
_EXTERNAL_SYSTEM_ERROR_LOGGER = None
_REMOTE_IO_WRITE_LOG_LOCK = multiprocessing.Lock()
_REMOTE_IO_READ_LOG_LOCK = multiprocessing.Lock()
_REMOTE_IO_WRITE_LOG_PATH = None
_REMOTE_IO_READ_LOG_PATH = None


def set_external_system_error_logger(logger):
    assert logger
    global _EXTERNAL_SYSTEM_ERROR_LOGGER
    _EXTERNAL_SYSTEM_ERROR_LOGGER = logger


def clear_external_system_error_logger():
    global _EXTERNAL_SYSTEM_ERROR_LOGGER
    _EXTERNAL_SYSTEM_ERROR_LOGGER = None


def set_remote_io_write_log_path(path):
    assert path
    global _REMOTE_IO_WRITE_LOG_PATH
    with _REMOTE_IO_WRITE_LOG_LOCK:
        _REMOTE_IO_WRITE_LOG_PATH = os.path.abspath(path)


def set_remote_io_read_log_path(path):
    assert path
    global _REMOTE_IO_READ_LOG_PATH
    with _REMOTE_IO_READ_LOG_LOCK:
        _REMOTE_IO_READ_LOG_PATH = os.path.abspath(path)


def on_system_error(identifier, detail):
    if _EXTERNAL_SYSTEM_ERROR_LOGGER:

        #  It's easily possible for 'detail' to exceed the length of
        #  command-line parameters allowed when calling out to a registered
        #  external system error logger.
        #
        #  Limit the amount of detail that will be sent to an arbitrary
        #  small number to prevent errors when reporting errors.
        #
        detail = detail[:160]

        phlsys_subprocess.run(
            _EXTERNAL_SYSTEM_ERROR_LOGGER,
            identifier,
            detail)


def _log_system_exception(identifier, detail, exception):
    message = detail + '\n' + repr(exception)
    on_system_error(identifier, message)


def on_retry_exception(identifier, detail, e, delay):

    if delay is not None:
        _LOGGER.warning(
            'on_retry_exception: during "{}" encountered exception "{}", '
            'will retry in {}. More detail: "{}".'.format(
                identifier, type(e).__name__, delay, detail),
            exc_info=1)
    else:
        _LOGGER.error(
            'on_retry_exception: during "{}" encountered exception "{}", '
            'will not retry. More detail: "{}".'.format(
                identifier, type(e).__name__, detail),
            exc_info=1)

    _log_system_exception(identifier, detail, e)


def _log_remote_io_event(prolog, identifier, detail, epilog, lock, path):
    with lock:
        if path:
            with open(path, 'a') as f:
                now = str(datetime.datetime.utcnow())
                description = '{}: ({}) {} - {} - ({})\n'.format(
                    now, prolog, identifier, detail, epilog)
                f.write(description)


@contextlib.contextmanager
def _remote_io_event_context(identifier, detail, lock, path):
    _log_remote_io_event('start', identifier, detail, '', lock, path)
    timer = phlsys_timer.Timer()
    timer.start()
    result_list = []
    try:
        yield result_list
    finally:
        prolog = '{:.3f}s'.format(timer.duration)
        _log_remote_io_event(
            prolog, identifier, detail, result_list, lock, path)


def remote_io_write_event_context(identifier, detail):
    return _remote_io_event_context(
        identifier,
        detail,
        _REMOTE_IO_WRITE_LOG_LOCK,
        _REMOTE_IO_WRITE_LOG_PATH)


def remote_io_read_event_context(identifier, detail):
    return _remote_io_event_context(
        identifier,
        detail,
        _REMOTE_IO_READ_LOG_LOCK,
        _REMOTE_IO_READ_LOG_PATH)


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
