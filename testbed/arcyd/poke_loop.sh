###############################################################################
# continuously poke reviews into arcyd and accept them
###############################################################################

set -e
trap "echo FAILED!; exit 1" EXIT

basedir=$(dirname "$0")  # directory the script lives in
arcyon="${basedir}/../../bin/arcyon"

phaburi="http://127.0.0.1"
aliceuser='alice'
alicecert=35yxukrjcltwgzfmgsnj2klc2jbrnzehqz3c36ijxnicwysv3xenxymwz532pyhimpxh\
7jryynh32su2ajxahd3gp7qshyik2qwf6ntuim2acxvjnko6p2q4mhacpvugqou2wpmyqwj4hkchgc\
5vh33lur723r4dexy5b3aj35v4v6ffork727ww5qk5yhhcmolbcqg3rxl6qpf53spn4aopneg\
gtb675hmpx3xya3et7jrowzlkl3yw3sktvdu

arcyoncreds="--uri ${phaburi} --user ${aliceuser} --cert ${alicecert}"

function poke() {
    feature=$(tr -dc "[:alpha:]" < /dev/urandom | head -c 8)
    branch="arcyd-review/${feature}/master"
    echo poke feature ${feature}
    git checkout -b ${branch} origin/master
    touch ${feature}
    git add .
    git commit -am "poked feature ${feature}"
    git push -u origin ${branch}
    sleep 1

    # find and accept most recent reviewable revision, if any
    revisionid=$(${arcyon} query --max-results 1 --statuses 'Needs Review' --format-type ids ${arcyoncreds})
    if [ -n "$revisionid" ]; then
        ${arcyon} comment ${revisionid} --action accept ${arcyoncreds}
    fi
}

while [ ! -f __kill_poke__ ]; do poke; done

trap - EXIT
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
