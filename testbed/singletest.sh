#!/bin/sh
if [ $# -ne 3 ]
then
    echo usage: singletest.sh MODULE TEST_CLASS TEST_NAME
    echo example: singletest.sh abdi_processrepo Test test_A_Breathing
    exit
fi
cd "$(git rev-parse --show-toplevel)"
package=`echo $1 | awk '{print substr($0,0,4)}'`
testsuffix="__t.py"
PYTHONPATH=py/phl:testbed/plugins nosetests --nocapture py/$package/$1$testsuffix:$2.$3
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
