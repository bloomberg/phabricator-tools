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
# :o  perform runtime(unit) tests                                             #
# :o  perform integration tests                                               #
# :o  perform smoke tests                                                     #
#                                                                             #
###############################################################################

function print_help {
    echo "Usage: $0 [-e TEST_NAME] [-h]"
    echo
    echo "-e: Takes as argument the name of the test to be excluded from being"
    echo "    run. If you want to exclude multiple tests, use this option those"
    echo "    many times. Valid values for this argument are 'gen_docs',"
    echo "    'autofix', 'static_tests', 'unit_tests' and 'smoke_tests'. Note"
    echo "    that it always raises an error if working directory is not clean"
    echo "    even if all tests are excluded."
    echo
    echo -h: Prints this help.
}

exclude_tests=()

while getopts "e:h" opt; do
    case $opt in
        e)
            exclude_tests+=("$OPTARG")
            ;;
        h)
            print_help
            exit 0
            ;;
        ?)
            echo
            print_help
            exit 1
            ;;
    esac
done

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

if [[ ! "${exclude_tests[@]}" =~ gen_doc ]]; then
    ###########################################################################
    # refresh the documentation
    ###########################################################################
    printf "gen_doc: "
    ./gen_doc.sh

    ###########################################################################
    # check that the working copy is clean after refreshing documentation
    ###########################################################################
    trap - ERR
    git diff --exit-code
    if [ "$?" -ne 0 ]; then
        echo
        echo The working copy is dirty after generating docs, please review and
        echo add the changes before continuing.
        exit -1
    fi
    trap 'echo FAIL; exit 1' ERR
    echo ' OK'
fi

if [[ ! "${exclude_tests[@]}" =~ autofix ]]; then
    ###########################################################################
    # perform automatic fixes of minor code issues
    ###########################################################################
    printf "autofix: "
    ./autofix.sh

    ###########################################################################
    # check that the working copy is clean after autofix
    ###########################################################################
    trap - ERR
    git diff --exit-code
    if [ "$?" -ne 0 ]; then
        echo
        echo The working copy is dirty after automatic fixes, please review and
        echo add the changes before continuing.
        exit -1
    fi
    trap 'echo FAIL; exit 1' ERR
    echo ' OK'
fi

if [[ ! "${exclude_tests[@]}" =~ static_tests ]]; then
    ###########################################################################
    # perform static analysis
    ###########################################################################
    printf "static tests: "
    ./static_tests.sh
    echo ' OK'
fi

if [[ ! "${exclude_tests[@]}" =~ unit_tests ]]; then
    ###########################################################################
    # perform run-time tests (unit-tests etc.)
    ###########################################################################
    printf "unit tests: "
    ./unit_tests.sh
    # echo ' OK' <-- nose will print status for itself
fi

if [[ ! "${exclude_tests[@]}" =~ integration_tests ]]; then
    ###########################################################################
    # perform run-time tests (integration-tests etc.)
    ###########################################################################
    printf "integration tests: "
    ./integration_tests.sh
    # echo ' OK' <-- nose will print status for itself
fi

if [[ ! "${exclude_tests[@]}" =~ smoke_tests ]]; then
    ###########################################################################
    # perform smoke tests (stuff in testbed/ etc.)
    ###########################################################################
    printf "smoke tests: "
    ./smoke_tests.sh
    echo ' OK'
fi

# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
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
