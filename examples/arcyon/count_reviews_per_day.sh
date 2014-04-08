# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

echo "last update time, counts per day:"
echo
tempfile=`mktemp`

arcyon query "$@" --format-string '$daysSinceDateModified' --max-results 2000 > $tempfile
arcyon query "$@" --format-string '$daysSinceDateModified' --max-results 2000 --offset-results 2000 >> $tempfile
arcyon query "$@" --format-string '$daysSinceDateModified' --max-results 2000 --offset-results 4000 >> $tempfile
arcyon query "$@" --format-string '$daysSinceDateModified' --max-results 2000 --offset-results 6000 >> $tempfile
arcyon query "$@" --format-string '$daysSinceDateModified' --max-results 2000 --offset-results 8000 >> $tempfile

uniq -c $tempfile
echo `wc -l < $tempfile` reviews considered
echo "(n.b. counts up to last 10,000 reviews or so only)"
rm $tempfile
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
