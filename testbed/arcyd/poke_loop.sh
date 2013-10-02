###############################################################################
# continuously poke reviews into arcyd and accept them
###############################################################################

set -e
trap "echo FAILED!; exit 1" EXIT

basedir=$(dirname "$0")  # directory the script lives in
arcyon="${basedir}/../../bin/arcyon"

phaburi="http://127.0.0.1"
arcyduser='phab'
arcydcert=xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrv\
afgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w\
6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk\
3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

arcyoncreds="--uri ${phaburi} --user ${arcyduser} --cert ${arcydcert}"

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
        ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
    fi
}

while [ ! -f __kill_poke__ ]; do poke; done

trap - EXIT
