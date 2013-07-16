# do tests in order of time to execute
trap 'echo FAIL; exit 1' ERR

# cd to the dir of this script, so we can run scripts in the same dir
cd "$(dirname "$0")"

trap - ERR
git diff --exit-code
if [ "$?" -ne 0 ]; then
    echo
    echo 'The working copy is dirty (see diff above)'
    echo
    echo If we have outstanding edits before generating docs then we could
    echo be in trouble as this may mean that we have edited generated files.
    echo Also, we want to make sure that we are testing what we are going
    echo to commit.
    echo
    echo Please add the changes before continuing.
    exit -1
fi
trap 'echo FAIL; exit 1' ERR

./gen_doc.sh

trap - ERR
git diff --exit-code
if [ "$?" -ne 0 ]; then
    echo
    echo The working copy is dirty after generating docs, please review and add
    echo the changes before continuing.
    exit -1
fi
trap 'echo FAIL; exit 1' ERR

./static_tests.sh
./runtime_tests.sh
