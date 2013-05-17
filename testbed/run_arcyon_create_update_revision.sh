trap "echo FAILED!" ERR
set -x

arcyon='../bin/arcyon'

id="$($arcyon create-revision -t title -p plan -f diff1)"
$arcyon update-revision -i $id -f diff2 -m update

$arcyon query --format-type ids | grep $id

diffid="$($arcyon raw-diff diff1)"
diffid2="$($arcyon raw-diff diff2)"
id2="$($arcyon create-revision -t title2 -p plan --diff-id $diffid)"
$arcyon update-revision -i $id2 -m update --diff-id $diffid2

$arcyon query --format-type ids | grep $id2

$arcyon comment $id2 -m 'hello there!'
