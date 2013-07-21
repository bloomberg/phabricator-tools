###############################################################################
## pre-commit operations and tests ############################################
#                                                                             #
# Run this script after adding all your changes to the index but preferably   #
# before committing them.                                                     #
#                                                                             #
# The script may make changes to the code, for example when generating        #
# documentation comment blocks.                                               #
#                                                                             #
# The following operations are performed:                                     #
# :o  check the working copy is clean                                         #
# :o  refresh documentation                                                   #
# :o  check the working copy is clean                                         #
# :o  perform automatic fixes of minor code issues                            #
# :o  check the working copy is clean                                         #
# :o  perform static analysis                                                 #
# :o  perform runtime tests                                                   #
#                                                                             #
###############################################################################

# in the event of an error, print 'FAIL' and exit with code 1
trap 'echo FAIL; exit 1' ERR

# cd to the dir of this script, so we can run scripts in the same dir
cd "$(dirname "$0")"

###############################################################################
# check that the working copy is clean
###############################################################################
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

###############################################################################
# refresh the documentation
###############################################################################
./gen_doc.sh

###############################################################################
# check that the working copy is clean after refreshing documentation
###############################################################################
trap - ERR
git diff --exit-code
if [ "$?" -ne 0 ]; then
    echo
    echo The working copy is dirty after generating docs, please review and add
    echo the changes before continuing.
    exit -1
fi
trap 'echo FAIL; exit 1' ERR

###############################################################################
# perform automatic fixes of minor code issues
###############################################################################
./autofix.sh

###############################################################################
# check that the working copy is clean after autofix
###############################################################################
trap - ERR
git diff --exit-code
if [ "$?" -ne 0 ]; then
    echo
    echo The working copy is dirty after automatic fixes, please review and add
    echo the changes before continuing.
    exit -1
fi
trap 'echo FAIL; exit 1' ERR

###############################################################################
# perform static analysis
###############################################################################
./static_tests.sh

###############################################################################
# perform run-time tests (unit-tests etc.)
###############################################################################
./runtime_tests.sh
