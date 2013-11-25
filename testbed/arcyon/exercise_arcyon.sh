trap "echo FAILED!; exit 1" ERR
set -x

arcyon='../../bin/arcyon'

$arcyon -h
$arcyon comment -h
$arcyon get-diff -h
$arcyon paste -h
$arcyon query -h
$arcyon raw-diff -h
$arcyon show-config -h
$arcyon update-revision -h
$arcyon task-create -h

id="$($arcyon create-revision -t title -p plan --summary ssss -f diff1)"
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
id2="$($arcyon create-revision -t title2 -p plan --diff-id $diffid)"
$arcyon update-revision $id2 update --diff-id $diffid2

$arcyon query --format-type ids | grep $id2

$arcyon comment $id2 -m 'hello there!'

$arcyon task-create 'exercise task-create'
$arcyon task-create 'exercise task-create' -d 'description' -p wish

$arcyon paste "test paste" -f diff1
