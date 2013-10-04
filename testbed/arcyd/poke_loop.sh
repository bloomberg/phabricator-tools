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
