"""Operations on git commit message strings."""


def make(title, summary, test_plan, reviewers):
    """Return string commit message.

    :title: string title of the commit (single line)
    :summary: string summary of the commit
    :reviewers: list of string reviewers
    :test_plan: string of the test plan
    :returns: string commit message

    """
    message = ""

    extra_fields = False  # the title will have a carriage return only if True

    if summary and summary.strip():
        extra_fields = True
        message += "\n" + summary
    if test_plan and test_plan.strip():
        extra_fields = True
        message += "\n" + "Test Plan:"
        message += "\n" + test_plan
    if reviewers:
        extra_fields = True
        message += "\n" + "Reviewers:"
        message += "\n" + ' '.join(reviewers)

    if extra_fields:
        message = title + "\n" + message
    else:
        message = title

    return message


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
