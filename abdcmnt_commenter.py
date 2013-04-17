import phlcon_differential
import phlcon_remarkup as rmu

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
            else:
                self._userException(e)
        else:
            message = "unhandled exception: " + str(e)
            self._createComment(message)

    def failedCreateReview(self, branch_name, exception):
        message = "failed to create revision from branch "
        message += rmu.monospaced(branch_name) + "\n"
        self._createComment(message)
        self.exception(exception)

    def _createComment(self, message):
        phlcon_differential.createComment(
            self._conduit, self._revision_id, message)

    def _commitMessageParseException(self, e):
        message = "failed to update revision, see below.\n"
        message += "\n"

        message += "errors:\n"
        for error in e.errors:
            message += rmu.codeBlock(str(error), lang="text", isBad=True)

        message += "fields:\n"
        message += rmu.dictToTable(e.fields)

        message += "combined commit message digest:\n"
        message += rmu.codeBlock(e.digest, lang="text")

        self._createComment(message)

    def _landingException(self, e):
        message = "failed to land revision, see below.\n"
        message += "\n"

        message += "errors:\n"
        message += rmu.codeBlock(str(e), lang="text", isBad=True)

        self._createComment(message)

    def _userException(self, e):
        message = "failed to update revision, see below.\n"
        message += "\n"

        message += "errors:\n"
        message += rmu.codeBlock(str(e), lang="text", isBad=True)

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
