trap "echo FAILED!; exit 1" ERR
set -x

barc='../../proto/barc'

$barc -h
$barc gc -h
