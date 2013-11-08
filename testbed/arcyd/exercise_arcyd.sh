set -x
set -e
trap "echo FAILED!; exit 1" EXIT

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

arcyd="$(pwd)/../../proto/arcyd"
arcyon="$(pwd)/../../bin/arcyon"
barc="$(pwd)/../../proto/barc"

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
$arcyd process-repos -h
$arcyd arcyd-status-html -h
$arcyd repo-status-html -h
$arcyd dev-status-html -h
$arcyd instaweb -h

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
    echo --review-url-format >> repo_arcyd.cfg
    echo 'http://my.phabricator/D{review}' >> repo_arcyd.cfg
    echo --branch-url-format >> repo_arcyd.cfg
    echo 'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}' >> repo_arcyd.cfg

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
    process-repos \
    --sys-admin-emails admin@server.test \
    --sendmail-binary ${mail} \
    --sendmail-type catchmail \
    --repo-configs @repo_arcyd.cfg \
    --status-path arcyd_status.json \
    --sleep-secs 0 \
    --no-loop

${arcyd} \
    arcyd-status-html \
    arcyd_status.json \
    https://server.test/arcyd

${arcyd} \
    repo-status-html \
    touches/repo_origin.try \
    touches/repo_origin.ok
}

setup_repos
configure_arcyd
run_arcyd

# exercise the killfile route
touch killfile
set +e
$arcyd \
    process-repos \
    --sys-admin-emails admin@server.test \
    --sendmail-binary ${mail} \
    --sendmail-type catchmail \
    --repo-configs @repo_arcyd.cfg \
    --status-path arcyd_status.json \
    --sleep-secs 0 \
    --kill-file killfile \
    --no-loop
set -e

# create a review branch
cd dev
    git checkout -b 'arcyd-review/myfile/master'
    echo hello > MYFILE
    git add MYFILE
    git commit -m 'exercise_arcyd: add MYFILE'
    git push origin 'arcyd-review/myfile/master'
cd -
run_arcyd

# update the review branch
cd dev
    echo goodbye > MYFILE
    git add MYFILE
    git commit -m 'update MYFILE'
    git push origin 'arcyd-review/myfile/master'
    git branch -r | grep 'origin/arcyd-review/myfile/master'
cd -
run_arcyd

# find and accept the review
revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
run_arcyd

# make sure the revision is closed and landed
${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Closed'
cd dev
    git fetch -p 2>&1 | grep 'deleted.*myfile'
cd -

# create a review branch as unknown user
cd dev
    git fetch
    git checkout -b 'arcyd-review/myfile2/master' origin/master
    git config user.name 'Unknown User'
    git config user.email 'unknown@server.test'
    echo GOODBYE > MYFILE
    git commit -am 'exercise_arcyd: bad author'
    git push origin 'arcyd-review/myfile2/master'
cd -
run_arcyd

# look for a bad author review
badauthor_revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
if [ ! ${badauthor_revisionid} = ${revisionid} ]; then
    echo 'FAILED! bad author created a review'
    exit 1
fi

# update review branch as user 'bob'
cd dev
    git config user.name 'Bob User'
    git config user.email 'bob@server.test'
    git commit --amend --reset-author --no-edit
    git push origin 'arcyd-review/myfile2/master' --force
cd -
run_arcyd

# look for a good author review
badauthor_revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
if [ ${badauthor_revisionid} = ${revisionid} ]; then
    echo 'FAILED! fixed bad author (bob) didnt create a review'
    exit 1
fi

# clean up the landed branches
cd dev
    git checkout master  # we can't remove the current branch, so be on master
    $barc gc --update --force
cd -

cat savemail.txt

cat touches/repo_origin.try
cat touches/repo_origin.ok

cd ${olddir}
rm -rf ${tempdir}
trap - EXIT
