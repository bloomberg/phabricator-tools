"""Render html to report the state of a repository watched by Arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdweb_repocontent
#
# Public Functions:
#   render
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import abdt_reporeporter


def render(formatter, repo_report, branch_report):

    if not repo_report and not branch_report:
        formatter.text('repo has never been tried')
        return

    if repo_report:
        repo_name = repo_report[abdt_reporeporter.REPO_ATTRIB_NAME]
        status = repo_report[abdt_reporeporter.REPO_ATTRIB_STATUS]
        branch = repo_report[abdt_reporeporter.REPO_ATTRIB_STATUS_BRANCH]
        status_text = repo_report[abdt_reporeporter.REPO_ATTRIB_STATUS_TEXT]

        formatter.heading(repo_name)
        formatter.text('status: ' + status)
        if branch:
            formatter.text('branch: ' + branch)
        if status_text:
            formatter.text('status text:\n' + status_text)


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
