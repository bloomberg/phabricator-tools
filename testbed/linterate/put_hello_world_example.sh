###############################################################################
# put the 'hello_world' files into a new review
###############################################################################

set -e
trap "echo FAILED!; exit 1" EXIT

basedir=$(dirname "$0")  # directory the script lives in
arcyon="${basedir}/../../bin/arcyon"

phaburi="http://127.0.0.1"
aliceuser='alice'
alicecert=35yxukrjcltwgzfmgsnj2klc2jbrnzehqz3c36ijxnicwysv3xenxymwz532pyhimpxh\
7jryynh32su2ajxahd3gp7qshyik2qwf6ntuim2acxvjnko6p2q4mhacpvugqou2wpmyqwj4hkchgc\
5vh33lur723r4dexy5b3aj35v4v6ffork727ww5qk5yhhcmolbcqg3rxl6qpf53spn4aopneg\
gtb675hmpx3xya3et7jrowzlkl3yw3sktvdu

arcyoncreds="--uri ${phaburi} --user ${aliceuser} --cert ${alicecert}"

git diff -U1000 --no-index -- hello_world.cpp hello_world_bad.cpp | ${arcyon} create-revision -f - -t 'hello world cpp test' -p 'UNTESTED' ${arcyoncreds}

trap - EXIT
