# do tests in order of time to execute
set -e # exit immediately on error

## please install pychecker with sudo apt-get install pychecker
# TODO: find workaround for borked import detection
# TODO: fix phlcon_differential.createDiff() to not have 16 params
pychecker \
    --quiet --only --no-import --exec --constant1 \
    --maxlines 150 --maxbranches 15 --maxreturns 5 --maxargs 16 --maxlocals 20\
    py/*.py

flake8 bin/*
flake8 py/*.py

# please install snakefood with ./doc/package_deps/install_snakefood.sh
sfood py/*.py --internal > doc/package_deps/deps
./doc/package_deps/process.py doc/package_deps/deps doc/package_deps/file-deps doc/package_deps/package-deps
diff ./doc/package_deps/expected-package-deps ./doc/package_deps/package-deps

# copyright
set +e

git grep -L "Copyright (C) 2012 Bloomberg L.P." py/*.py
if [ $? -ne 1 ]
then
    echo -- above files are missing copyright notice --
    exit 1
fi
git grep -L "Copyright (C) 2012 Bloomberg L.P." bin/*
if [ $? -ne 1 ]
then
    echo -- above files are missing copyright notice --
    exit 1
fi

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

