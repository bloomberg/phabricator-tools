###############################################################################
## integration tests ##########################################################
#                                                                             #
# The following tests are performed:                                          #
# :o integration-tests, discovered and run using nose                         #
#                                                                             #
# N.B. you can pass parameters to nose, e.g. to re-run failed tests only:     #
# $ ./integration_tests.sh --failed                                           #
#                                                                             #
###############################################################################

set -e # exit immediately on error

# cd to the dir of this script, so we can run scripts in the same dir
cd "$(dirname "$0")"

# only test 'library' scripts for now
it_libscripts="$(find py -iname '*__it.py')"

###############################################################################
# integration-tests
###############################################################################

# 'sudo apt-get install python-nose' or use the commented-out version
# 'sudo apt-get install python-coverage' to use the '--with-coverage' option
# the '--with-profile' option should just work
# the '--failed' option will run only the tests that failed on the last run

PYTHONPATH=py/phl:py/abd:testbed/plugins nosetests $it_libscripts "$@"

#python -m unittest discover -p "*.py"
# N.B. can easily run individual tests with nose like so:
# nosetests abdcmd_default:TestAbd.test_abandonedWorkflow
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
