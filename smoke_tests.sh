###############################################################################
## system tests ###############################################################
#                                                                             #
# The following tests are performed:                                          #
# :o scripted system tests under 'testbed/'                                   #
#                                                                             #
###############################################################################

set -e # exit immediately on error

# cd to the dir of this script, so we can run scripts in the same dir
cd "$(dirname "$0")"

###############################################################################
# exercisers / system tests
###############################################################################

function run_test_script() {
    local workingdir=$1
    local scriptname=$2
    set +e
    OUTPUT=$(cd ${workingdir}; ./${scriptname} 2>&1)
    if [ $? -ne 0 ]
    then
        echo ==================================================================
        echo -- \'${scriptname}\' failed, see errors below
        echo ------------------------------------------------------------------
        echo
        echo "$OUTPUT"
        echo
        echo ------------------------------------------------------------------
        echo -- \'${scriptname}\' failed, see errors above
        echo ==================================================================
        exit 1
    fi
    set -e # exit immediately on error
    printf "."
}

run_test_script "testbed/arcyd" "exercise_arcyd.sh"
run_test_script "testbed/arcyon" "exercise_arcyon.sh"
run_test_script "testbed/barc" "smoketest.sh"
run_test_script "testbed/git-phab-log" "smoketest.sh"
run_test_script "testbed/conduit-proxy" "smoketest.sh"
run_test_script "testbed/arcyd-tester" "smoketest.sh"
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
