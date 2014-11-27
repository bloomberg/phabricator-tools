"""Log important events appropriately from anywhere in Arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_logging
#
# Public Functions:
#   arcyd_reporter_context
#   set_arcyd_reporter
#   clear_arcyd_reporter
#   set_external_system_error_logger
#   clear_external_system_error_logger
#   on_system_error
#   on_retry_exception
#   on_review_event
#   on_io_event
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import logging

import phlsys_subprocess


_LOGGER = logging.getLogger(__name__)
_REPORTER = None
_EXTERNAL_SYSTEM_ERROR_LOGGER = None


@contextlib.contextmanager
def arcyd_reporter_context(reporter):
    set_arcyd_reporter(reporter)
    try:
        yield
    finally:
        clear_arcyd_reporter()


def set_arcyd_reporter(reporter):
    assert reporter
    global _REPORTER
    _REPORTER = reporter


def clear_arcyd_reporter():
    global _REPORTER
    _REPORTER = None


def _get_reporter():
    reporter = _REPORTER
    if reporter is None:
        _LOGGER.error("no reporter is set")
    return reporter


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

    reporter = _get_reporter()
    if reporter:
        reporter.on_tryloop_exception(e, delay)
        _log_system_exception(identifier, detail, e)


def on_review_event(identifier, detail):
    reporter = _get_reporter()
    if reporter:
        reporter.log_user_action(identifier, detail)


def on_io_event(identifier, detail):
    reporter = _get_reporter()
    if reporter:
        reporter.log_io_action(identifier, detail)


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
