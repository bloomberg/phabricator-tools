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
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import logging

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
        logging.error("no reporter is set")
    return reporter


def on_retry_exception(identifier, detail, e, delay):
    logging.error(str(e) + "\nwill wait " + str(delay))
    reporter = _get_reporter()
    if reporter:
        _REPORTER.on_tryloop_exception(e, delay)
        _REPORTER.log_system_exception(identifier, detail, e)


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
