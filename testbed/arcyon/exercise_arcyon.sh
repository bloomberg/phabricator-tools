trap "echo 'FAILED!'; exit 1" ERR
set -x

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

arcyon='../../bin/arcyon'

$arcyon -h
$arcyon comment -h
$arcyon comment-inline -h
$arcyon get-diff -h
$arcyon paste -h
$arcyon query -h
$arcyon raw-diff -h
$arcyon show-config -h
$arcyon update-revision -h
$arcyon task-create -h
$arcyon task-query -h

id="$($arcyon create-revision -t title -p plan --summary ssss -f diff1 --format-id)"
$arcyon get-diff -r $id --ls
$arcyon update-revision $id update -f diff2
$arcyon get-diff -r $id --ls

$arcyon query --format-type ids | grep $id
$arcyon query --ids $id --format-string '$summary' | grep ssss
$arcyon query --format-type ids --order created | grep $id
$arcyon query --format-type ids --order modified | grep $id

diffid="$($arcyon raw-diff diff1)"
diffid2="$($arcyon raw-diff diff2)"
$arcyon get-diff -d $diffid --ls
$arcyon get-diff -d $diffid2 --ls
id2="$($arcyon create-revision -t title2 -p plan --diff-id $diffid --format-id)"
id3=$($arcyon update-revision $id2 update --diff-id $diffid2 --format-id)
$arcyon update-revision $id2 update --diff-id $diffid2 --format-url

if [ "$id2" != "$id3" ]; then
    false
fi

$arcyon query --format-type ids | grep $id2

$arcyon comment $id2 -m 'hello there!'
$arcyon comment-inline $id2 --start-line 51 --end-line-offset 0 --filepath 'bin/arcyon' -m 'inline comment!'
$arcyon comment-inline $id2 --start-line 51 --end-line-offset 0 --filepath 'bin/arcyon' -m 'old-side inline comment!' --left-side
$arcyon comment $id2 --attach-inlines

taskid=$($arcyon task-create 'exercise task-create' -d 'description' -p wish -o alice --ccs phab bob --format-id)
$arcyon task-query
taskid2=$($arcyon task-query --max-results 1 --format-ids)

if [ "$taskid" != "$taskid2" ]; then
    false
fi

$arcyon task-create 'exercise task-create again'
$arcyon task-update $taskid -m 'just a comment'
$arcyon task-update $taskid -t 'exercise task-update' -d 'new description' -p low -o bob --ccs phab alice -m 'updated loads'

$arcyon paste "test paste" -f diff1
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
