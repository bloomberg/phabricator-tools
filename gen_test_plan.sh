###############################################################################
## generate test plan #########################################################
#                                                                             #
# The following operations are performed:                                     #
# :o update 'test plan' documentation at the top of each test fixture         #
#                                                                             #
# N.B. paths to scripts for which test plan needs to be generated need to be  #
# passed as arguments to this script                                          #
#                                                                             #
###############################################################################

set -e # exit immediately on error

# cd to the dir of this script, so we can run scripts in the same dir
cd "$(dirname "$0")"

###############################################################################
# update 'test plan' documentation at the top of each test fixture
###############################################################################

python meta/docgen/updatetestplan.py --force-insert "$@"
printf "."


# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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
