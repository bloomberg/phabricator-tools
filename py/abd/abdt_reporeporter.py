"""Report the state of a repository."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_reporeporter
#
# Public Classes:
#   SharedFileDictOutput
#    .write
#   SharedDictOutput
#    .write
#   RepoReporter
#    .on_tryloop_exception
#    .on_exception
#    .on_completed
#    .start_branch
#    .finish_branch
#    .close
#
# Public Assignments:
#   REPO_ATTRIB_NAME
#   REPO_ATTRIB_STATUS
#   REPO_LIST_ATTRIB
#   REPO_STATUS_UPDATING
#   REPO_STATUS_FAILED_TRYLOOP
#   REPO_STATUS_FAILED_EXCEPTION
#   REPO_STATUS_FAILED
#   REPO_STATUS_OK
#   REPO_STATUSES
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import json

import phlsys_fs

REPO_ATTRIB_NAME = 'name'
REPO_ATTRIB_STATUS = 'status'

REPO_LIST_ATTRIB = [
    REPO_ATTRIB_NAME,
    REPO_ATTRIB_STATUS,
]

REPO_STATUS_UPDATING = 'updating'
REPO_STATUS_FAILED_TRYLOOP = 'failed tryloop'
REPO_STATUS_FAILED_EXCEPTION = 'failed exception'
REPO_STATUS_FAILED = 'failed'
REPO_STATUS_OK = 'ok'

REPO_STATUSES = [
    REPO_STATUS_UPDATING,
    REPO_STATUS_FAILED_TRYLOOP,
    REPO_STATUS_FAILED_EXCEPTION,
    REPO_STATUS_FAILED,
    REPO_STATUS_OK,
]


class SharedFileDictOutput(object):

    def __init__(self, filename):
        super(SharedFileDictOutput, self).__init__()
        self._filename = filename

    def write(self, d):
        assert isinstance(d, dict)
        with phlsys_fs.write_file_lock_context(self._filename) as f:
            f.write(json.dumps(d))


class SharedDictOutput(object):

    def __init__(self, shared_d):
        super(SharedDictOutput, self).__init__()
        self._shared_d = shared_d
        assert isinstance(self._shared_d, dict)

    def write(self, d):
        assert isinstance(d, dict)
        # copy contents to other dict
        self._shared_d.clear()
        self._shared_d.update(d)


class RepoReporter(object):

    def __init__(self, repo_name, try_output, ok_output):
        """Initialise a new reporter to report to the specified outputs.

        :repo_name: human-readable name to identify the repo
        :try_output: output to use when trying the repo
        :ok_output: output to use when processed the repo

        """
        super(RepoReporter, self).__init__()
        self._try_output = try_output
        self._ok_output = ok_output
        self._is_updating = True

        assert self._try_output
        assert self._ok_output

        self._repo_attribs = {
            REPO_ATTRIB_NAME: repo_name,
        }

        self._update_write_repo_status(REPO_STATUS_UPDATING)

    def on_tryloop_exception(self, e, delay):
        self._repo_report(str(e) + "\nwill wait " + str(delay))
        self._is_updating = False
        self._update_write_repo_status(REPO_STATUS_FAILED_TRYLOOP)

    def on_exception(self, e):
        self._repo_report(str(e))
        self._is_updating = False
        self._update_write_repo_status(REPO_STATUS_FAILED_EXCEPTION)

    def on_completed(self):
        self._ok_output.write({})
        self._is_updating = False
        self._update_write_repo_status(REPO_STATUS_OK)

    def start_branch(self, branch):
        _ = branch  # NOQA
        self._repo_report('start branch')

    def finish_branch(self, branch):
        _ = branch  # NOQA
        self._repo_report('finish branch')

    def _update_write_repo_status(self, status):
        self._repo_attribs[REPO_ATTRIB_STATUS] = status
        self._try_output.write(self._repo_attribs)

    def _repo_report(self, s):
        pass

    def close(self):
        """Close any resources associated with the report."""
        self._is_updating = False
        if self._is_updating:
            self._update_write_repo_status(REPO_STATUS_FAILED)


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
