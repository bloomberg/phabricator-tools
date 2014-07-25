# comment 'nudge' on reviews which we've been waiting on for over 2 days

# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

minage="2 days"
ids1=`arcyon query "$@" --author-me --status-type open --statuses 'Needs Review' --format-type ids --update-min-age "$minage"`
ids2=`arcyon query "$@" --reviewer-me --status-type open --statuses 'Needs Revision' --format-type ids --update-min-age "$minage"`

echo "will comment 'nudge' on the following reviews:"
ids=`echo $ids1 $ids2`
echo $ids

read -p "Hit 'y' to continue or any other to exit: " choice
if [ ! "$choice" = "y" ]; then
    echo user aborted.
    exit 2
fi

arcyon comment $ids "$@" -m 'nudge'
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
