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


_LOGGER = logging.getLogger(__name__)
_REPORTER = None


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
        reporter.log_system_exception(identifier, detail, e)


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
