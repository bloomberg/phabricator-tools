"""Operations on git commit message strings."""

import unittest


def _makeSection(section_name, content):
    wrap_len = 72
    line = section_name + ": " + content
    if len(line.splitlines()) == 1 and len(line) < wrap_len:
        section = line
    else:
        section = section_name + ":\n"
        section += content
    return section


def make(title, summary, test_plan, reviewers):
    """Return string commit message.

    :title: string title of the commit (single line)
    :summary: string summary of the commit
    :reviewers: list of string reviewers
    :test_plan: string of the test plan
    :returns: string commit message

    """
    message = title

    if summary and summary.strip():
        message += "\n\n" + summary
    if test_plan and test_plan.strip():
        test_section = _makeSection("Test Plan", test_plan)
        message += "\n\n" + test_section
    if reviewers:
        reviewers_content = ' '.join(reviewers)
        reviewers_section = _makeSection("Reviewers", reviewers_content)
        if test_plan and len(test_section.splitlines()) == 1:
            # we can keep the test plan and reviewers together if both
            # are only using a single line each
            message += "\n" + reviewers_section
        else:
            message += "\n\n" + reviewers_section

    return message


class TestCommitMessage(unittest.TestCase):

    # TODO: this belongs in a string helper module
    def _stripLines(self, s):
        s = s.strip()
        s = [l.strip() for l in s.splitlines()]
        return '\n'.join(s)

    def testJustTitle(self):
        msg = make("title", None, None, None)
        self.assertSequenceEqual("title", msg)

    def testSummary(self):
        msg = make("title", "summary", None, None)
        self.assertSequenceEqual("title\n\nsummary", msg)

    def testTitleMultilineSummary(self):
        msg = make("title", "summary\nsummary2", None, None)
        self.assertSequenceEqual("title\n\nsummary\nsummary2", msg)

    def testTitleMultilineSummaryTestPlan(self):
        msg = make("title", "summary\nsummary2", "plan", None)
        emsg = """
            title

            summary
            summary2

            Test Plan: plan
            """
        self.assertSequenceEqual(self._stripLines(emsg), msg)

    def testLongTestPlanLine(self):
        long_plan = "this is a long plan that is certainly too long to fit" * 2
        long_plan = long_plan * 2
        msg = make("title", None, long_plan, None)
        emsg = """
            title

            Test Plan:
            """ + long_plan
        self.assertSequenceEqual(self._stripLines(emsg), msg)

    def testMultilineTestPlan(self):
        multiline_plan = "my test plan\ngoes over\na few lines"
        msg = make("title", None, multiline_plan, None)
        emsg = """
            title

            Test Plan:
            """ + multiline_plan
        self.assertSequenceEqual(self._stripLines(emsg), msg)

    def testMultilineTestPlanReviewers(self):
        multiline_plan = "my test plan\ngoes over\na few lines"
        msg = make("title", None, multiline_plan, ["reviewer"])
        emsg = """
            title

            Test Plan:
            """ + multiline_plan + """

            Reviewers: reviewer
            """
        self.assertSequenceEqual(self._stripLines(emsg), msg)

    def testCompactReviewers(self):
        msg = make("title", None, "plan", ["reviewer"])
        emsg = """
            title

            Test Plan: plan
            Reviewers: reviewer
            """
        self.assertSequenceEqual(self._stripLines(emsg), msg)

    def testAllTogether(self):
        msg = make("title", "summary", "plan", ["reviewer"])
        emsg = """
            title

            summary

            Test Plan: plan
            Reviewers: reviewer
            """
        self.assertSequenceEqual(self._stripLines(emsg), msg)


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
