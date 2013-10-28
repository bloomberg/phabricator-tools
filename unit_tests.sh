###############################################################################
## unit tests #################################################################
#                                                                             #
# The following tests are performed:                                          #
# :o unit-tests and doc-tests, discovered and run using nose                  #
#                                                                             #
# N.B. you can pass parameters to nose, e.g. to re-run failed tests only:     #
# $ ./runtime_tests.sh --failed                                               #
#                                                                             #
###############################################################################

set -e # exit immediately on error

# cd to the dir of this script, so we can run scripts in the same dir
cd "$(dirname "$0")"

# only test 'library' scripts for now
libscripts="$(find py -iname '*.py')"

###############################################################################
# unit-tests and doc-tests
###############################################################################

# 'sudo apt-get install python-nose' or use the commented-out version
# 'sudo apt-get install python-coverage' to use the '--with-coverage' option
# the '--with-profile' option should just work
# the '--failed' option will run only the tests that failed on the last run

PYTHONPATH=py/phl:py/abd:testbed/plugins nosetests $libscripts --with-doctest --doctest-tests "$@"

#python -m unittest discover -p "*.py"
# N.B. can easily run individual tests with nose like so:
# nosetests abdcmd_default:TestAbd.test_abandonedWorkflow
