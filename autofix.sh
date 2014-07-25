###############################################################################
## automatic code fixes #######################################################
#                                                                             #
# The following operations are performed:                                     #
# :o autopep8 (linter)                                                        #
# :o docformatter (linter)                                                    #
# :o fiximports (linter)                                                      #
# :o fixlegal (linter)                                                        #
#                                                                             #
###############################################################################

set -e # exit immediately on error

# cd to the dir of this script, so we can run scripts in the same dir
cd "$(dirname "$0")"

# distinguish between 'library' scripts and all scripts
libscripts=$(find py/ -iname '*.py' |  tr '\n' ' ')
allscripts="$(ls bin/* proto/* meta/docgen/*.py) $libscripts"

###############################################################################
# autopep8
###############################################################################
autopep8 --in-place $allscripts
printf "."

###############################################################################
# docformatter
###############################################################################
docformatter -i $allscripts
printf "."

###############################################################################
# sort imports
###############################################################################
python meta/autofix/fiximports.py $libscripts
printf "."

###############################################################################
# fix legal notices
###############################################################################
python meta/autofix/fixlegal.py . --different-since origin/master
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
