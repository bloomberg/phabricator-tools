"""Mock version of abdt_reporeporter for testing."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_reporeportermock
#
# Public Classes:
#   RepoReporterMock
#    .on_tryloop_exception
#    .on_exception
#    .on_completed
#    .start_branch
#    .finish_branch
#    .close
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================


class RepoReporterMock(object):

    def __init__(self):
        """Initialise a new reporter to report to the specified files.

        :try_filename: string path to the file to touch when trying the repo
        :ok_filename: string path to the file to touch when processed the repo

        """
        super(RepoReporterMock, self).__init__()

    def on_tryloop_exception(self, e, delay):
        _ = self, e, delay  # NOQA

    def on_exception(self, e):
        _ = self, e  # NOQA

    def on_completed(self):
        _ = self  # NOQA

    def start_branch(self, branch):
        _ = self, branch  # NOQA

    def finish_branch(self, branch):
        _ = self, branch  # NOQA

    def _repo_report(self, s):
        _ = self, s  # NOQA

    def close(self):
        """Close any resources associated with the report."""
        _ = self  # NOQA


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
