trap "echo FAILED!; exit 1" ERR
set -x

gab='../../proto/git-phab-log'

$gab -h
