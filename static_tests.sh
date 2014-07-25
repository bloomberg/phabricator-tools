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
