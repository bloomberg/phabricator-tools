trap "echo FAILED!; exit 1" ERR
set -x

arcyd="$(pwd)/../../proto/arcyd"
arcyon="$(pwd)/../../bin/arcyon"

phaburi="http://127.0.0.1"
arcyduser='phab'
arcydcert=xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrv\
afgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w\
6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk\
3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

arcyoncreds="--uri ${phaburi} --user ${arcyduser} --cert ${arcydcert}"

mail="$(pwd)/savemail"

tempdir=$(mktemp -d)
olddir=$(pwd)
cd ${tempdir}

$arcyd -h
$arcyd multi -h

function setup_repos() {
    mkdir origin
    cd origin
    git init --bare
    cd ..

    git clone origin dev
    cd dev
    touch README
    git add README
    git commit -m 'intial commit'
    git push origin master
    git config user.name 'Bob User'
    git config user.email 'bob@server.test'
    cd ..

    git clone origin arcyd
}

function configure_arcyd() {
    mkdir -p touches

    touch repo_arcyd.cfg
    echo @instance_local.cfg >> repo_arcyd.cfg
    echo @email_arcyd.cfg >> repo_arcyd.cfg
    echo @email_admin.cfg >> repo_arcyd.cfg
    echo --repo-desc >> repo_arcyd.cfg
    echo arcyd test >> repo_arcyd.cfg
    echo --repo-path >> repo_arcyd.cfg
    echo arcyd >> repo_arcyd.cfg
    echo --try-touch-path >> repo_arcyd.cfg
    echo touches/repo_origin.try >> repo_arcyd.cfg
    echo --ok-touch-path >> repo_arcyd.cfg
    echo touches/repo_origin.ok >> repo_arcyd.cfg

    touch instance_local.cfg
    echo --instance-uri >> instance_local.cfg
    echo http://127.0.0.1/api/ >> instance_local.cfg
    echo --arcyd-user >> instance_local.cfg
    echo phab >> instance_local.cfg
    echo --arcyd-cert >> instance_local.cfg
    echo xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrvafgzqu\
zl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w6lcseh\
s2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk3lyr3u\
vot7fxrotwpi3ty2b2sa2kvlpf >> instance_local.cfg

    touch email_arcyd.cfg
    echo --arcyd-email >> email_arcyd.cfg
    echo phab-role-account@server.example >> email_arcyd.cfg

    touch email_arcyd.cfg
    echo --admin-email >> email_admin.cfg
    echo admin@server.example >> email_admin.cfg
}

function run_arcyd() {
$arcyd \
    multi \
    --sys-admin-emails admin@server.test \
    --sendmail-binary ${mail} \
    --sendmail-type catchmail \
    --repo-configs @repo_arcyd.cfg \
    --sleep-secs 0 \
    --no-loop

}

setup_repos
configure_arcyd
run_arcyd

# create a review branch
cd dev
    git checkout -b 'ph-review/myfile/master'
    echo hello > MYFILE
    git add MYFILE
    git commit -m 'add MYFILE'
    git push origin 'ph-review/myfile/master'
cd -
run_arcyd


cd dev
    echo goodbye > MYFILE
    git add MYFILE
    git commit -m 'update MYFILE'
    git push origin 'ph-review/myfile/master'
    git branch -r | grep 'origin/ph-review/myfile/master'
cd -
run_arcyd

revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
run_arcyd

# make sure the revision is closed and landed
${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Closed'
cd dev
    git fetch -p 2>&1 | grep 'deleted.*myfile'
cd -

cat savemail.txt

cat touches/repo_origin.try
cat touches/repo_origin.ok

cd ${olddir}
rm -rf ${tempdir}
