"""Make pre-defined comments on Differential revisions."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmnt_commenter
#
# Public Classes:
#   Commenter
#    .exception
#    .failedCreateReview
#    .createdReview
#    .updatedReview
#    .landedReview
#    .abandonedBranch
#    .usedDefaultTestPlan
#    .removedSelfReviewer
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

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
            elif isinstance(e, abdt_exception.LandingPushBaseException):
                self._landingPushBaseException(e)
            elif isinstance(e, abdt_exception.LandingException):
                self._landingException(e)
            elif isinstance(e, abdt_exception.LargeDiffException):
                self._diffException(e)
            elif isinstance(e, abdt_exception.MissingBaseException):
                self._missingBaseException(e)
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

    def createdReview(
            self, repo_name, branch_name, base_name, branch_url=None):

        message = """
created revision from:

**repository**: {repo_name}
**branch**: {branch_name}

if the revision is accepted then i will automatically try to land the
revision on {base_name}.

the commit message will be created from the title, summary, test plan and
other properties of this review page.

the author may change the properties of the review at any time by following
the 'edit revision' link at the top-right of the page.
        """.format(
            repo_name=phlcon_remarkup.monospaced(repo_name),
            branch_name=phlcon_remarkup.monospaced(branch_name),
            base_name=phlcon_remarkup.monospaced(base_name)).strip()

        if branch_url is not None:
            message += "\n\n"
            message += "you can browse {name} here:\n{url}".format(
                name=phlcon_remarkup.monospaced(branch_name),
                url=phlcon_remarkup.link(branch_url))

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
        message += "\n"
        message += "if this review is accepted then nothing will be landed "
        message += "because there is no associated branch.\n"
        message += "\n"
        message += "if the branch is pushed again, then a completely new "
        message += "review will be created.\n"
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

    def removedSelfReviewer(self, branch_name, digest):
        digest_markup = phlcon_remarkup.code_block(
            digest, lang="text", isBad=True)

        branch_markup = phlcon_remarkup.monospaced(branch_name)

        message = (
            "author, you added yourself to the list of reviewers in your "
            "commit message.\n"
            "\n"
            "phabricator does not permit the author of a review to also be a "
            "reviewer.\n"
            "\n"
            "please carefully review the current list of reviewers to make "
            "sure there are no other errors.\n"
            "\n"
            "combined message digest from branch {branch}:\n"
            "{digest}").format(branch=branch_markup, digest=digest_markup)

        self._createComment(message)

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
        errors = phlcon_remarkup.code_block(str(e), lang="text", isBad=True)
        reviewer = phlcon_remarkup.bold('reviewer')

        message = (
            "failed to land revision on {base}, see below.\n"
            "\n"
            "errors:\n"
            "{errors}"
            "this is probably due to merge conflicts.\n"
            "\n"
            "{author}, please do the following:\n"
            "\n"
            "- merge {base} into {branch}\n"
            "- resolve merge conflicts\n"
            "- push to {branch}\n"
            "\n"
            "{reviewer} may then accept review with the new changes.\n"
        ).format(
            base=base,
            branch=branch,
            author=author,
            errors=errors,
            reviewer=reviewer)

        self._createComment(message)

    def _landingPushBaseException(self, e):
        base = phlcon_remarkup.monospaced(e.base_name)
        branch = phlcon_remarkup.monospaced(e.review_branch_name)
        author = phlcon_remarkup.bold('author')
        errors = phlcon_remarkup.code_block(str(e), lang="text", isBad=True)
        reviewer = phlcon_remarkup.bold('reviewer')

        message = (
            "failed to push landed revision to {base}, see below.\n"
            "\n"
            "errors:\n"
            "{errors}"
            "this might be down to permissioning or maybe someone else "
            "updated the branch before we pushed.\n"
            "\n"
            "if there's a permissioning error then please ask the admin of "
            "this repository to resolve it before proceeding.\n"
            "\n"
            "{reviewer} may accept review again to retry the landing.\n"
        ).format(
            base=base,
            branch=branch,
            author=author,
            errors=errors,
            reviewer=reviewer)

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

    def _missingBaseException(self, e):
        field_table = phlcon_remarkup.dict_to_table({
            'description': e.description,
            'base': e.base_name})
        remove_instructions = phlcon_remarkup.code_block(
            "git push origin :{branch}".format(branch=e.review_branch_name),
            lang="shell")
        message = (
            "the specified base branch does not exist: {base}\n"
            "\n"
            "the 'base' is the branch to diff against and to land on when "
            "the review is approved.\n"
            "\n"
            "here's how the branch name {branch} was interpreted:\n"
            "{field_table}\n"
            "as author you should clean up like so:\n"
            "\n"
            "- abandon this review using the 'comment' drop down at the "
            "bottom of this page.\n"
            "- remove the associated review branch like so:\n"
            "{remove_instructions}\n"
            "in the future please ensure that the base branch exists "
            "before creating a review to land on it."
        ).format(
            base=phlcon_remarkup.monospaced(e.base_name),
            branch=phlcon_remarkup.monospaced(e.review_branch_name),
            field_table=field_table,
            remove_instructions=remove_instructions)

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
