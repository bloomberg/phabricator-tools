trap "echo 'FAILED!'; exit 1" ERR
set -x

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

arcyon='../../bin/arcyon'

taskid=$($arcyon task-create 'exercise task-create' -d 'description' -p wish -o alice --ccs phab bob --format-id)

# exercise task-query thoroughly
$arcyon task-query
$arcyon task-query --order priority
$arcyon task-query --order created
$arcyon task-query --order modified
$arcyon task-query --order title
$arcyon task-query --max-results 1
$arcyon task-query --offset-results 1
$arcyon task-query --offset-results 1 --max-results 1
$arcyon task-query --priorities wish low normal high triage unbreak_now
$arcyon task-query --priorities wish
$arcyon task-query --priorities low
$arcyon task-query --text description
$arcyon task-query --status any
$arcyon task-query --status open
$arcyon task-query --status closed
$arcyon task-query --status resolved
$arcyon task-query --status wontfix
$arcyon task-query --status invalid
$arcyon task-query --status spite
$arcyon task-query --status duplicate

$arcyon query --branch mybranch

# -----------------------------------------------------------------------------
# Copyright (C) 2014-2015 Bloomberg Finance L.P.
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
