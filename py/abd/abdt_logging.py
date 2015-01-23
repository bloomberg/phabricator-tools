"""Log important events appropriately from anywhere in Arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_logging
#
# Public Functions:
#   set_external_system_error_logger
#   clear_external_system_error_logger
#   on_system_error
#   on_retry_exception
#   remote_io_write_event_context
#   remote_io_read_event_context
#   misc_operation_event_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
import logging

import phlsys_subprocess
import phlsys_timer


_LOGGER = logging.getLogger(__name__)
_EXTERNAL_SYSTEM_ERROR_LOGGER = None


def set_external_system_error_logger(logger):
    assert logger
    global _EXTERNAL_SYSTEM_ERROR_LOGGER
    _EXTERNAL_SYSTEM_ERROR_LOGGER = logger


def clear_external_system_error_logger():
    global _EXTERNAL_SYSTEM_ERROR_LOGGER
    _EXTERNAL_SYSTEM_ERROR_LOGGER = None


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


def _log_remote_io_event_to_logger(
        kind, prolog, identifier, detail, epilog, logger):

    entry = '{}: ({}) {} - {} - ({})'.format(
        kind, prolog, identifier, detail, epilog)

    logger(entry)


@contextlib.contextmanager
def _remote_io_event_log_context(kind, identifier, detail, logger):
    _log_remote_io_event_to_logger(
        kind, 'start', identifier, detail, '', logger)
    timer = phlsys_timer.Timer()
    timer.start()
    result_list = []
    try:
        yield result_list
    finally:
        prolog = '{:.3f}s'.format(timer.duration)
        _log_remote_io_event_to_logger(
            kind, prolog, identifier, detail, result_list, logger)


def remote_io_write_event_context(identifier, detail):
    return _remote_io_event_log_context(
        'io-write-event', identifier, detail, _LOGGER.info)


def remote_io_read_event_context(identifier, detail):
    return _remote_io_event_log_context(
        'io-read-event', identifier, detail, _LOGGER.debug)


def misc_operation_event_context(identifier, detail):
    return _remote_io_event_log_context(
        'misc-event', identifier, detail, _LOGGER.debug)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
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
