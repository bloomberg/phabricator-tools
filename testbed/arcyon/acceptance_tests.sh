trap "echo 'FAILED!'; exit 1" ERR
set -x

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

arcyon='../../bin/arcyon'

taskid=$($arcyon task-create 'exercise task-create' -d 'description' -p wish -o alice --ccs phab bob --format-id)

# exercise task-query thoroughly
$arcyon task-query
$arcyon task-query --order priority
$arcyon task-query --order created
$arcyon task-query --order modified
$arcyon task-query --order title
$arcyon task-query --max-results 1
$arcyon task-query --offset-results 1
$arcyon task-query --offset-results 1 --max-results 1
$arcyon task-query --priorities wish low normal high triage unbreak_now
$arcyon task-query --priorities wish
$arcyon task-query --priorities low
$arcyon task-query --text description
$arcyon task-query --status any
$arcyon task-query --status open
$arcyon task-query --status closed
$arcyon task-query --status resolved
$arcyon task-query --status wontfix
$arcyon task-query --status invalid
$arcyon task-query --status spite
$arcyon task-query --status duplicate
# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
