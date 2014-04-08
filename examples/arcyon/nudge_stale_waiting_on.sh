# comment 'nudge' on reviews which we've been waiting on for over 2 days

# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

minage="2 days"
ids1=`arcyon query "$@" --author-me --status-type open --statuses 'Needs Review' --format-type ids --update-min-age "$minage"`
ids2=`arcyon query "$@" --reviewer-me --status-type open --statuses 'Needs Revision' --format-type ids --update-min-age "$minage"`

echo "will comment 'nudge' on the following reviews:"
ids=`echo $ids1 $ids2`
echo $ids

read -p "Hit 'y' to continue or any other to exit: " choice
if [ ! "$choice" = "y" ]; then
    echo user aborted.
    exit 2
fi

arcyon comment $ids "$@" -m 'nudge'
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
