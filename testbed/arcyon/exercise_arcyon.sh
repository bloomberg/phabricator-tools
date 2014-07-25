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
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
