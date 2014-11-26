set -x
set -e
trap "echo FAILED!; exit 1" EXIT

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

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
$arcyd init -h
$arcyd add-phabricator -h
$arcyd add-repohost -h
$arcyd add-repo -h
$arcyd start -h
$arcyd stop -h
$arcyd list-repos -h
$arcyd fetch -h

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
}

function configure_arcyd() {
    mkdir arcyd_instance
    cd arcyd_instance

    $arcyd init \
        --arcyd-email 'arcyd@localhost' \
        --sleep-secs 0 \
        --sendmail-binary ${mail} \
        --sendmail-type catchmail

    $arcyd add-phabricator \
        --name localhost \
        --instance-uri http://127.0.0.1/api/ \
        --review-url-format 'http://my.phabricator/D{review}' \
        --arcyd-user phab \
        --arcyd-cert \
xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrvafgzqu\
zl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w6lcseh\
s2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk3lyr3u\
vot7fxrotwpi3ty2b2sa2kvlpf

    $arcyd add-repohost \
        --name fs \
        --repo-url-format '../{}' \
        --branch-url-format 'http://my.git/gitweb?p={repo_url}.git;a=log;h=refs/heads/{branch}' \
        --admin-email 'local-repo-admin@localhost'

    $arcyd add-repo localhost fs origin

    cd ..
}

function run_arcyd() {
cd arcyd_instance

${arcyd} start --no-loop --foreground

cd ..
}

setup_repos
configure_arcyd
run_arcyd

# exercise the stop route
echo exercise the stop route
cd arcyd_instance
${arcyd} start
sleep 1
${arcyd} stop
cd ..

# exercise 'list-repos'
cd arcyd_instance
${arcyd} list-repos
${arcyd} list-repos --only-formatted-repo-urls
cd ..

# exercise 'fsck'
cd arcyd_instance
${arcyd} fsck
${arcyd} fsck --fix
cd ..

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
    git fetch origin refs/arcyd/landed:refs/arcyd/landed
    git branch --merged refs/arcyd/landed | grep -v '*' | xargs git branch -D
cd -

cat arcyd_instance/savemail.txt

cat arcyd_instance/var/status/localhost_fs_origin.try
cat arcyd_instance/var/status/localhost_fs_origin.ok

# exercise 'rm-repo'
cd arcyd_instance
${arcyd} rm-repo localhost_fs_origin
git show
cd ..

cd ${olddir}
rm -rf ${tempdir}
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
