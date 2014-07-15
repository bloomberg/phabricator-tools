###############################################################################
## static analysis tests ######################################################
#                                                                             #
# The following tests are performed:                                          #
# :o pychecker (linter)                                                       #
# :o flake8 (linter)                                                          #
# :o check dependencies between packages, using snakefood                     #
# :o check for components which are unused by end products, using snakefood   #
#                                                                             #
###############################################################################

set -e # exit immediately on error

# cd to the dir of this script, so we can run scripts in the same dir
cd "$(dirname "$0")"

# distinguish between 'library' scripts and all scripts
libscripts=$(find py/ -iname '*.py' |  tr '\n' ' ')
allscripts="$(ls bin/* proto/* meta/docgen/*.py meta/autofix/*.py) $libscripts"

###############################################################################
# pylint
###############################################################################
PYTHONPATH=py/phl pylint \
    --rcfile=.pylint.rc \
    --errors-only \
    ${libscripts}
printf "."

###############################################################################
# pychecker
###############################################################################

## please install pychecker with sudo apt-get install pychecker
# TODO: find workaround for borked import detection
# TODO: fix phlcon_differential.createDiff() to not have 16 params
PYTHONPATH=py/phl:py/abd pychecker \
    --quiet --only --no-import --exec --constant1 --initattr --changetypes \
    --no-deprecated \
    --maxlines 150 --maxbranches 15 --maxreturns 5 --maxargs 16 --maxlocals 20\
    ${libscripts}
printf "."

###############################################################################
# flake8
###############################################################################
flake8 $allscripts
printf "."

###############################################################################
# check dependencies between packages
###############################################################################

# please install snakefood with ./meta/package_deps/install_snakefood.sh
sfood ${libscripts} --internal > meta/package_deps/deps
./meta/package_deps/process.py meta/package_deps/deps meta/package_deps/file-deps meta/package_deps/package-deps
diff ./meta/package_deps/expected-package-deps ./meta/package_deps/package-deps
printf "."

###############################################################################
# check for unused components
###############################################################################
(cd meta/package_deps; ./check_no_dead_files.sh)
printf "."

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
