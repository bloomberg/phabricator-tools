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
# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# ------------------------------ END-OF-FILE ----------------------------------
