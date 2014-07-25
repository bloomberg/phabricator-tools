# Check the requirements for the other examples to be able to run

# make sure that the arcyon binary can be found
find_binary=$(which arcyon)
if [[ $? != 0 ]] ; then
    echo could not find arcyon binary, please add it to your '$PATH'
    echo
    echo [FAILED]
    exit 1
else
    echo found arcyon:
    echo $find_binary
fi

echo

# let 'arcyon show-config' determine if the configuration is sufficient
# it will print helpful error messages if not and exit non-zero
trap 'echo;echo [FAILED]; exit 1' ERR
arcyon show-config "$@"

echo
echo [OK]
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
