"""Make pre-defined comments on Differential revisions."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmnt_commenter
#
# Public Classes:
#   Commenter
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

import phlcon_remarkup

import abdt_exception


class Commenter(object):

    """Make pre-defined comments on Differential revisions."""

    def __init__(self, conduit, revision_id):
        """Initialise, simply store the supplied parameters.

        :conduit: the conduit to send comments to
        :revision_id: int revision id to comment on

        """
        self._conduit = conduit
        self._revision_id = revision_id

    def exception(self, e):
        if isinstance(e, abdt_exception.AbdBaseException):
            if isinstance(e, abdt_exception.CommitMessageParseException):
                self._commitMessageParseException(e)
            elif isinstance(e, abdt_exception.LandingException):
                self._landingException(e)
            elif isinstance(e, abdt_exception.LargeDiffException):
                self._diffException(e)
            else:
                self._userException(e)
        else:
            message = "unhandled exception: " + str(e)
            self._createComment(message)

    def failedCreateReview(self, branch_name, exception):
        message = "failed to create revision from branch "
        message += phlcon_remarkup.monospaced(branch_name) + "\n"
        self._createComment(message)
        self.exception(exception)

    def createdReview(self, branch_name, base_name):
        message = "created revision from branch "
        message += phlcon_remarkup.monospaced(branch_name) + "\n"
        message += "\n"
        message += "if the revision is accepted then i will automatically try "
        message += "to land the revision on "
        message += phlcon_remarkup.monospaced(base_name) + "."
        message += " the commit message will "
        message += "be created from the title, summary, test plan and other "
        message += "properties of this review page.\n"
        message += "\n"
        message += "the author may change the properties of the review at any "
        message += "time by following the 'edit revision' link at the "
        message += "top-right of the page."
        self._createComment(message, silent=True)

    def updatedReview(self, branch_name):
        message = "updated revision from branch "
        message += phlcon_remarkup.monospaced(branch_name) + "\n"
        self._createComment(message, silent=True)

    def landedReview(self, branch_name, base_name, git_output):
        message = "landed "
        message += phlcon_remarkup.monospaced(branch_name) + " "
        message += " on "
        message += phlcon_remarkup.monospaced(base_name) + "\n"
        message += "deleted " + phlcon_remarkup.monospaced(branch_name) + "\n"
        message += "git output:\n"
        message += phlcon_remarkup.code_block(git_output, lang="text")
        self._createComment(message, silent=True)

    def abandonedBranch(self, branch_name):
        message = "user deleted branch "
        message += phlcon_remarkup.monospaced(branch_name) + " "
        message += "which was linked to this review.\n"
        message += "this review is now abandoned."
        self._createComment(message, silent=True)

    def usedDefaultTestPlan(self, branch_name, test_plan):
        message = "a test plan could not be determined from the commits on "
        message += phlcon_remarkup.monospaced(branch_name) + " "
        message += "so the following message was used:\n"
        message += phlcon_remarkup.code_block(test_plan, lang="text")
        message += "for a test plan to be recognised, please use text like "
        message += "the following in your latest commit message: \n"
        message += phlcon_remarkup.code_block(
            "Test Plan:\nmy test plan", lang="text")
        message += "as author you may edit the test plan directly by "
        message += "using the 'edit revision' link at the top-right of "
        message += "this review page."
        self._createComment(message, silent=True)

    def _createComment(self, message, silent=False):
        self._conduit.create_comment(self._revision_id, message, silent=silent)

    def _commitMessageParseException(self, e):
        message = "errors were encountered, see below.\n"
        message += "\n"

        message += "errors:\n"
        for error in e.errors:
            message += phlcon_remarkup.code_block(
                str(error), lang="text", isBad=True)

        message += "fields:\n"
        message += phlcon_remarkup.dict_to_table(e.fields)

        message += "combined commit message digest:\n"
        message += phlcon_remarkup.code_block(e.digest, lang="text")

        self._createComment(message)

    def _landingException(self, e):
        base = phlcon_remarkup.monospaced(e.base_name)
        branch = phlcon_remarkup.monospaced(e.review_branch_name)
        author = phlcon_remarkup.bold('author')
        reviewer = phlcon_remarkup.bold('reviewer')

        message = "failed to land revision on " + base + ", see below.\n"
        message += "\n"
        message += "errors:\n"
        message += phlcon_remarkup.code_block(str(e), lang="text", isBad=True)
        message += "this is probably due to merge conflicts.\n"
        message += "\n"
        message += author + ", please do the following:\n"
        message += "\n"
        message += "- merge " + base + " into " + branch + "\n"
        message += "- resolve merge conflicts\n"
        message += "- push to " + branch + "\n"
        message += "\n"
        message += reviewer + " may then accept review with the new changes.\n"

        self._createComment(message)

    def _diffException(self, e):
        message = str("failed to create diff, tried to reduce context but it "
                      "was still too large.\n")
        message += "\n"
        message += "diff size: " + str(e.diff_len) + " bytes\n"
        message += "diff size limit: " + str(e.diff_len_limit) + " bytes\n"
        message += "summary:\n"
        message += phlcon_remarkup.code_block(
            str(e.diff_summary), lang="text", isBad=True)

        self._createComment(message)

    def _userException(self, e):
        message = "errors were encountered, see below.\n"
        message += "\n"

        message += "errors:\n"
        message += phlcon_remarkup.code_block(str(e), lang="text", isBad=True)

        self._createComment(message)


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
