# exit with error message if anything returns error status
trap 'echo FAILED; exit 1' ERR

echo "last update time, counts per week:"
echo
tempfile=`mktemp`

arcyon query "$@" --format-string '$weeksSinceDateModified' --max-results 2000 > $tempfile
arcyon query "$@" --format-string '$weeksSinceDateModified' --max-results 2000 --offset-results 2000 >> $tempfile
arcyon query "$@" --format-string '$weeksSinceDateModified' --max-results 2000 --offset-results 4000 >> $tempfile
arcyon query "$@" --format-string '$weeksSinceDateModified' --max-results 2000 --offset-results 6000 >> $tempfile
arcyon query "$@" --format-string '$weeksSinceDateModified' --max-results 2000 --offset-results 8000 >> $tempfile

uniq -c $tempfile
echo `wc -l < $tempfile` reviews considered
echo "(n.b. counts up to last 10,000 reviews or so only)"
rm $tempfile
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
