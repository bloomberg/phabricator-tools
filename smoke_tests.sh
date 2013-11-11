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
}

run_test_script "testbed/arcyd" "exercise_arcyd.sh"
run_test_script "testbed/arcyon" "exercise_arcyon.sh"
run_test_script "testbed/barc" "smoketest.sh"
run_test_script "testbed/git-phab-log" "smoketest.sh"
