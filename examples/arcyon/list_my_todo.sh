# List out the revisions that require the user to act next.

# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

#TODO: echo Your revisions in review with no reviewers:
#TODO: $arcyon query --author-me --no-reviewers --status-type open --statuses 'Needs Review'

echo Revisions you have authored:
arcyon query "$@" --author-me --status-type open --statuses Accepted 'Needs Revision'

echo

echo Revisions you are reviewing:
arcyon query "$@" --reviewer-me --status-type open --statuses 'Needs Review'
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
