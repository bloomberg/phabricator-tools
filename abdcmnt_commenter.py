import phlcon_differential

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
                self.commitMessageParseException(e)
            elif isinstance(e, abdt_exception.LandingException):
                self.landingException(e)
            else:
                self.userException(e)
        else:
            message = "unhandled exception: " + str(e)
            phlcon_differential.createComment(
                self._conduit, self._revision_id, message)

    def commitMessageParseException(self, e):
        message = "failed to update revision, see below."
        message += "\n"

        message += "\nerrors:"
        message += "\n"
        message += "\n  lang=text"
        for error in e.errors:
            message += "\n  " + error
        message += "\n"

        message += "\nfields:"
        message += "\n"
        message += "\n  lang=text"
        for field, content in e.fields.items():
            message += "\n  " + field + ": " + str(content)
        message += "\n"

        message += "\ncombined commit message digest:"
        message += "\n"
        message += "\n  lang=text"
        for line in e.digest.splitlines():
            message += "\n  " + line

        phlcon_differential.createComment(
            self._conduit, self._revision_id, message)

    def landingException(self, e):
        message = "failed to land revision, see below."
        message += "\n"

        message += "\nerrors:"
        message += "\n"
        message += "\n  lang=text"
        for line in str(e).splitlines():
            message += "\n  " + line
        message += "\n"

        phlcon_differential.createComment(
            self._conduit, self._revision_id, message)

    def userException(self, e):
        message = "failed to update revision, see below."
        message += "\n"

        message += "\nerrors:"
        message += "\n"
        message += "\n  lang=text"
        for line in str(e).splitlines():
            message += "\n  " + line
        message += "\n"

        phlcon_differential.createComment(
            self._conduit, self._revision_id, message)


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
