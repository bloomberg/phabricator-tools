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

libscripts="$(find py -iname '*.py')"

# unittest
# 'sudo apt-get install python-nose' or use the commented-out version
# 'sudo apt-get install python-coverage' to use the '--with-coverage' option
# the '--with-profile' option should just work
# the '--failed' option will run only the tests that failed on the last run
PYTHONPATH=py/phl nosetests $libscripts --with-doctest --doctest-tests
#python -m unittest discover -p "*.py"

# N.B. can easily run individual tests with nose like so:
# nosetests abdcmd_default:TestAbd.test_abandonedWorkflow
