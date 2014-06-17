"""Make pre-defined comments on Differential revisions."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdcmnt_commenter
#
# Public Classes:
#   Commenter
#    .exception
#    .userWarnings
#    .failedCreateReview
#    .createdReview
#    .updatedReview
#    .landedReview
#    .abandonedBranch
#    .usedDefaultTestPlan
#    .removedSelfReviewer
#    .unknownReviewers
#    .largeDiff
#    .abandonedForUser
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import phlcon_remarkup

import abdt_differ
import abdt_exception
import abdt_userwarning

_ABANDONED_MESSAGE = """
this review has been abandoned, the review branch will be automatically
removed soon.

please change the state of the review to something other than 'abandoned' to
prevent automatic removal.
""".strip()

_NO_HISTORY_MESSAGE = """
there are no commits on `{review_branch}` that aren't also on `{base_branch}`.

this means that there is no history on the branch that can be reviewed.

it may also mean that the author of this review has been set incorrectly, as
i guessed and used the author of the latest commit on `{base_branch}`.

most likely `{review_branch}` was pushed before it had any commits on it to
review.

if the author has been set incorrectly then please either find the real author
and ask them to commandeer the review, or set the review to 'abandoned' and it
will automatically be archived.

""".strip()

_NO_DIFF_MESSAGE = """
there is no difference from `{base_branch}` to `{review_branch}`,
this means that there is nothing on the branch that can be reviewed.

`{review_branch}` is currently pointing to commit `{review_hash}`.

**author**, if you push to the branch again with new commits then the review
will be updated with the new diff.

""".strip()

_ABANDONED_FOR_USER_MESSAGE = """
i archived `{review_branch}` for you.
i am no longer watching this review.

if you want to re-create the review branch then you can follow these steps:

  $ git fetch origin {archive_ref}:{archive_ref}
  $ git branch {review_branch} {review_hash}

if this review is accepted then nothing will be landed.

if the branch is pushed again then a completely new review will be created.
""".strip()


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
            elif isinstance(e, abdt_exception.ReviewAbandonedException):
                self._reviewAbandonedException()
            elif isinstance(e, abdt_exception.NoHistoryException):
                self._noHistoryException(e)
            elif isinstance(e, abdt_exception.NoDiffException):
                self._noDiffException(e)
            else:
                self._userException(e)
        else:
            message = "unhandled exception: " + str(e)
            self._createComment(message)

    def userWarnings(self, user_warning_list):
        for warning in user_warning_list:
            if isinstance(warning, abdt_userwarning.UsedDefaultTestPlan):
                self.usedDefaultTestPlan(warning.default_message)
            elif isinstance(warning, abdt_userwarning.SelfReviewer):
                self.removedSelfReviewer(warning.user, warning.commit_message)
            elif isinstance(warning, abdt_userwarning.UnknownReviewers):
                self.unknownReviewers(
                    warning.unknown_reviewers, warning.commit_message)
            elif isinstance(warning, abdt_userwarning.LargeDiff):
                self.largeDiff(
                    warning.diff_result)
            else:
                message = "unhandled user warning: " + str(warning)
                self._createComment(message)

    def failedCreateReview(
            self, repo_name, branch_hash, branch_name, branch_url, exception):

        message = """
failed to create revision from:

**repository**: {repo_name}
**branch**: {branch_name}
**commit**: {branch_hash}
        """.format(
            repo_name=phlcon_remarkup.monospaced(repo_name),
            branch_name=phlcon_remarkup.monospaced(branch_name),
            branch_hash=phlcon_remarkup.monospaced(branch_hash)).strip()

        if branch_url is not None:
            message += "\n\n"
            message += "you can browse {name} here:\n{url}".format(
                name=phlcon_remarkup.monospaced(branch_name),
                url=phlcon_remarkup.link(branch_url))

        self._createComment(message)
        self.exception(exception)

    def createdReview(
            self,
            repo_name,
            branch_hash,
            branch_name,
            base_name,
            branch_url=None):

        message = """
created revision from:

**repository**: {repo_name}
**branch**: {branch_name}
**commit**: {branch_hash}

if the revision is accepted then i will automatically try to land the
revision on {base_name}.

the commit message will be created from the title, summary, test plan and
other properties of this review page.

the author may change the properties of the review at any time by following
the 'edit revision' link at the top-right of the page.
        """.format(
            repo_name=phlcon_remarkup.monospaced(repo_name),
            branch_name=phlcon_remarkup.monospaced(branch_name),
            branch_hash=phlcon_remarkup.monospaced(branch_hash),
            base_name=phlcon_remarkup.monospaced(base_name)).strip()

        if branch_url is not None:
            message += "\n\n"
            message += "you can browse {name} here:\n{url}".format(
                name=phlcon_remarkup.monospaced(branch_name),
                url=phlcon_remarkup.link(branch_url))

        self._createComment(message, silent=True)

    def updatedReview(self, branch_hash, branch_name):
        message = "updated revision from branch "
        message += phlcon_remarkup.monospaced(branch_name) + "\n"
        message += "to commit "
        message += phlcon_remarkup.monospaced(branch_hash) + "\n"
        self._createComment(message, silent=True)

    def landedReview(self, branch_hash, branch_name, base_name, git_output):
        message = "landed "
        message += phlcon_remarkup.monospaced(branch_name) + " "
        message += " on "
        message += phlcon_remarkup.monospaced(base_name) + "\n"
        message += "original commit "
        message += phlcon_remarkup.monospaced(branch_hash) + "\n"
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

    def usedDefaultTestPlan(self, test_plan):
        message = "a test plan could not be determined from the commits on "
        message += "the review branch, so the following message was used:\n"
        message += phlcon_remarkup.code_block(test_plan, lang="text")
        message += "for a test plan to be recognised, please use text like "
        message += "the following in your latest commit message: \n"
        message += phlcon_remarkup.code_block(
            "Test Plan:\nmy test plan", lang="text")
        message += "as author you may edit the test plan directly by "
        message += "using the 'edit revision' link at the top-right of "
        message += "this review page."
        self._createComment(message, silent=True)

    def removedSelfReviewer(self, user, commit_message):
        commit_message_markup = phlcon_remarkup.code_block(
            commit_message, lang="text", isBad=True)

        message = (
            "{user}, you added yourself to the list of reviewers in your "
            "commit message.\n"
            "\n"
            "phabricator does not permit the author of a review to also be a "
            "reviewer.\n"
            "\n"
            "please carefully review the current list of reviewers to make "
            "sure there are no other errors.\n"
            "\n"
            "commit message from branch:\n"
            "{commit_message}").format(
            user=user, commit_message=commit_message_markup)

        self._createComment(message)

    def unknownReviewers(self, unknown_reviewers, commit_message):
        unknown_users_markup = phlcon_remarkup.code_block(
            ', '.join(unknown_reviewers),
            lang="text",
            isBad=True)

        commit_message_markup = phlcon_remarkup.code_block(
            commit_message, lang="text", isBad=True)

        message = (
            "some reviewers specified in the commit message are unknown\n"
            "{unknown_users_block}"
            "please carefully review the current list of reviewers to make "
            "sure there are no other errors.\n"
            "\n"
            "commit message from branch:\n"
            "{commit_message}").format(
            unknown_users_block=unknown_users_markup,
            commit_message=commit_message_markup)

        self._createComment(message)

    def largeDiff(self, diff_result):
        message_list = []

        is_very_large = any(
            isinstance(r, abdt_differ.DiffStatReduction)
            for r in diff_result.reduction_list)

        if is_very_large:
            message_list.append(
                "**this diff is very large**, attempted a number of "
                "reduction techniques before managing to upload it.\n")

            message_list.append(
                "| **full diff size** | `{full_diff:,}` bytes, as UTF-8 |\n"
                "| **diff size limit** | `{max_diff:,}` bytes, as UTF-8 |\n"
                "| **end diff size** | `{diff:,}` bytes, as UTF-8 |\n".format(
                    full_diff=diff_result.full_diff_size_utf8_bytes,
                    max_diff=diff_result.max_diff_size_utf8_bytes,
                    diff=diff_result.diff_size_utf8_bytes))
        else:
            message_list.append(
                "**this diff is large**, attempted a number of "
                "reduction techniques before managing to upload it.\n")

        if diff_result.did_replace_unicode:
            message_list.append(
                "also, replaced some characters that could not be converted "
                "to unicode.\n")

        if is_very_large:
            message_list.append(
                "**if approved**, the change will land as normal with the "
                "full original content.\n")

        message_list.append(
            "here are the techniques that were attempted:\n")

        technique_list = []

        for r in diff_result.reduction_list:
            assert isinstance(r, abdt_differ.ReductionTechnique)
            if isinstance(r, abdt_differ.LessContextReduction):
                technique_list.append(
                    "tried to reduce the amount of context to "
                    "**{context:,} lines**, this reduced the diff size to "
                    "**{size:,} bytes** as UTF-8.".format(
                        context=r.context_lines,
                        size=r.diff_size_utf8_bytes))
            elif isinstance(r, abdt_differ.RemoveContextReduction):
                technique_list.append(
                    "tried to **remove all context**, this reduced the "
                    "diff size to "
                    "**{size:,} bytes** as UTF-8.".format(
                        size=r.diff_size_utf8_bytes))
            elif isinstance(r, abdt_differ.DiffStatReduction):
                technique_list.append(
                    "tried to reduce the diff to a **diffstat** instead, "
                    "this won't be reviewable but will give you an impression "
                    "of the change and what's biggest.")
            else:
                technique_list.append(
                    "tried an unknown reduction technique.")

        # add the techniques as a bulleted list
        message_list.append(
            ''.join(["- {}\n".format(t) for t in technique_list]))

        if is_very_large:
            message_list.append(
                "you may be able to reduce the diff size yourself by setting "
                "the `.gitattributes` of some files as `-diff`, this is often "
                "appropriate for generated files.\n")

            message_list.append(
                "e.g. commit a file like this to your project:\n")

            message_list.append(
                "  name=.gitattributes\n"
                "  path/to/large_generated_file -diff\n")

            message_list.append(
                "a fuller explanation Git Attributes may be found here: "
                "http://git-scm.com/book/ch7-2.html\n")

        self._createComment('\n'.join(message_list))

    def abandonedForUser(self, review_branch, review_hash, archive_ref):

        message = _ABANDONED_FOR_USER_MESSAGE.format(
            review_branch=review_branch,
            archive_ref=archive_ref,
            review_hash=review_hash)

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

    def _reviewAbandonedException(self):
        self._createComment(_ABANDONED_MESSAGE)

    def _noHistoryException(self, e):
        self._createComment(_NO_HISTORY_MESSAGE.format(
            review_branch=e.review_branch_name,
            base_branch=e.base_name))

    def _noDiffException(self, e):
        self._createComment(_NO_DIFF_MESSAGE.format(
            review_hash=e.review_branch_hash,
            review_branch=e.review_branch_name,
            base_branch=e.base_name))

    def _userException(self, e):
        message = "errors were encountered, see below.\n"
        message += "\n"

        message += "errors:\n"
        message += phlcon_remarkup.code_block(str(e), lang="text", isBad=True)

        self._createComment(message)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
# ------------------------------ END-OF-FILE ----------------------------------
