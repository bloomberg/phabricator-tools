# do tests in order of time to execute
set -e # exit immediately on error

flake8 bin/*
flake8 py/*.py

# please install snakefood with ./doc/package_deps/install_snakefood.sh
sfood py/*.py --internal > deps
./doc/package_deps/process.py deps file-deps package-deps
diff expected-package-deps package-deps

# unittest
# 'sudo apt-get install python-nose' or use the commented-out version
# 'sudo apt-get install python-coverage' to use the '--with-coverage' option
# the '--with-profile' option should just work
# the '--failed' option will run only the tests that failed on the last run
nosetests py/*.py --with-doctest
#python -m unittest discover -p "*.py"

# N.B. can easily run individual tests with nose like so:
# nosetests abdcmd_default:TestAbd.test_abandonedWorkflow

# copyright
git grep -L "Copyright (C) 2012 Bloomberg L.P." py/*.py
git grep -L "Copyright (C) 2012 Bloomberg L.P." bin/*

#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
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
#------------------------------- END-OF-FILE ----------------------------------
