###############################################################################
# acceptance tests for Arcyd, aimed at a more comprehensive coverage at the
# cost of a longer running time.
###############################################################################

set -x  # echo all commands to the terminal
set -e  # exit with error if anything returns non-zero
set -u  # exit with error if we use an undefined variable
set -o pipefail  # exit with error if any part of a pipe fails
trap "echo FAILED!; exit 1" EXIT

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

arcyd="$(pwd)/../../proto/arcyd"
arcyon="$(pwd)/../../bin/arcyon"
mail="$(pwd)/savemail"

phaburi="http://127.0.0.1"
arcyduser='phab'
arcydcert=xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrv\
afgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w\
6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk\
3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

arcyoncreds="--uri ${phaburi} --user ${arcyduser} --cert ${arcydcert}"

# here $1 is 'base' and $2 is 'description
classic_arcyd_branch_awk_string='{ printf "arcyd-review/%s/%s", $2, $1 }'
r_arcyd_branch_awk_string='{ printf "r/%s/%s", $1, $2 }'
arcyd_branch_awk_string="${classic_arcyd_branch_awk_string}"

function set_branch_name() {
    base=$1
    description=$2

    # here $1 is 'base' and $2 is 'description
    branch_name=$(echo "${base} ${description}" | awk "${arcyd_branch_awk_string}")
}

function setup_repos() {
    mkdir origin
    cd origin
    git init --bare
    cd ..

    git clone origin dev
    cd dev

    # write the initial commit
    git config user.name 'Bob User'
    git config user.email 'bob@server.test'
    touch README
    git add README
    git commit -m 'intial commit'
    git push origin master

    cd ..
}

function configure_arcyd() {
    mkdir arcyd
    cd arcyd

    $arcyd init \
        --sleep-secs 0 \
        --arcyd-email 'arcyd@localhost' \
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
    cd arcyd

    ${arcyd} start --no-loop --foreground
    echo $?

    ${arcyd} \
        arcyd-status-html \
        var/status/arcyd_status.json \
        https://server.test/arcyd
    echo $?

    ${arcyd} \
        repo-status-html \
        var/status/localhost_fs_origin.try \
        var/status/localhost_fs_origin.ok
    echo $?

    cd ..
}


function create_review_branch() {
    local branch_name=$1
    local file_name=$2
    cd dev
        git checkout -b ${branch_name} origin/master
        echo hello > ${file_name}
        git add ${file_name}
        git commit -m "acceptance_tests: ${file_name}"
        git push origin ${branch_name}
    cd -
}

function test_happy_path() {
    test_name='test_happy_path'
    set_branch_name "master" "${test_name}"

    # create a review branch
    create_review_branch "${branch_name}" "${test_name}"

    run_arcyd

    # update the review branch
    cd dev
        echo goodbye > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 2"
        git push origin ${branch_name}
        git branch -r | grep "origin/${branch_name}"
    cd -
    run_arcyd

    # update the review branch
    cd dev
        echo au reviour > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 3"
        echo adio > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 4"
        git push origin ${branch_name}
        git branch -r | grep "origin/${branch_name}"
    cd -
    run_arcyd

    # find and accept the review
    revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
    run_arcyd

    # make sure the revision is closed and landed
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Closed'
    cd dev
        deleted_prefix='deleted.*'
        git fetch -p 2>&1 | grep "${deleted_prefix}${branch_name}"
    cd -
}

function test_large_add() {
    test_name='test_large_add'
    set_branch_name "master" "${test_name}"

    # create a review branch with a very large new file
    cd dev
        git checkout -b ${branch_name} origin/master
        echo hello, this is a large file > ${test_name}
        for i in {1..16}; do
            cat ${test_name} ${test_name} > temp && mv temp ${test_name}
        done
        ls -lh
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name}"
        git push origin ${branch_name}
    cd -
    run_arcyd

    # update the review branch
    cd dev
        echo extra line >> ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 2"
        git push origin ${branch_name}
        git branch -r | grep "origin/${branch_name}"
    cd -
    run_arcyd

    # update the review branch
    cd dev
        echo another extra line >> ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 3"
        echo last extra line >> ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 4"
        git push origin ${branch_name}
        git branch -r | grep "origin/${branch_name}"
    cd -
    run_arcyd

    # find and accept the review
    revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
    run_arcyd

    # make sure the revision is closed and landed
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Closed'
    cd dev
        deleted_prefix='deleted.*'
        git fetch -p 2>&1 | grep "${deleted_prefix}${branch_name}"
    cd -
}

function test_large_file_small_change() {
    test_name='test_large_file_small_change'
    set_branch_name "master" "${test_name}"

    # create a very large new file on master
    cd dev
        git checkout master
        git pull
        echo hello, this is a large file > ${test_name}
        for i in {1..16}; do
            cat ${test_name} ${test_name} > temp && mv temp ${test_name}
        done
        ls -lh
        git add ${test_name}
        git commit -m "exercise_arcyd: add ${test_name}"
        git push origin master
    cd -

    cd dev
        git checkout -b ${branch_name} origin/master
        echo first extra line >> ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: small change to ${test_name}"
        git push origin ${branch_name}
    cd -
    run_arcyd

    # update the review branch
    cd dev
        echo extra line >> ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 2"
        git push origin ${branch_name}
        git branch -r | grep "origin/${branch_name}"
    cd -
    run_arcyd

    # update the review branch
    cd dev
        echo another extra line >> ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 3"
        echo last extra line >> ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 4"
        git push origin ${branch_name}
        git branch -r | grep "origin/${branch_name}"
    cd -
    run_arcyd

    # find and accept the review
    revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
    run_arcyd

    # make sure the revision is closed and landed
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Closed'
    cd dev
        deleted_prefix='deleted.*'
        git fetch -p 2>&1 | grep "${deleted_prefix}${branch_name}"
    cd -
}

function test_unknown_user() {
    test_name='test_unknown_user'
    set_branch_name "master" "${test_name}"

    # record the id of the last review, so we can see if we create a new one or not
    revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})

    # create a review branch as unknown user
    cd dev
        git fetch
        git checkout -b ${branch_name} origin/master
        git config user.name 'Unknown User'
        git config user.email 'unknown@server.test'
        echo hello > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name}"
        git push origin ${branch_name}
    cd -
    run_arcyd

    # look for a bad author review
    badauthor_revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    if [ ! ${badauthor_revisionid} = ${revisionid} ]; then
        echo 'FAILED! bad author created a review'
        exit 1
    fi

    # update review branch as another unknown user, use amend so that
    # if Arcyd doesn't force push the tracking branch then it will fail
    cd dev
        git config user.name 'Other Unknown User'
        git config user.email 'other.unknown@server.test'
        git commit --amend --reset-author --no-edit
        git push origin ${branch_name} --force
    cd -
    run_arcyd

    # update review branch as known user
    cd dev
        git config user.name 'Bob User'
        git config user.email 'bob@server.test'
        git commit --amend --reset-author --no-edit
        git push origin ${branch_name} --force
    cd -
    run_arcyd

    # look for a good author review
    badauthor_revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    if [ ${badauthor_revisionid} = ${revisionid} ]; then
        echo 'FAILED! fixed bad author didnt create a review'
        exit 1
    fi

    # make sure arcyd can process the review
    run_arcyd
}

function test_unknown_reviewer() {
    test_name='test_unknown_reviewer'
    set_branch_name "master" "${test_name}"

    # create a review branch
    cd dev
        git checkout -b ${branch_name} origin/master
        echo hello > ${test_name}
        git add ${test_name}
        commit_message="exercise_arcyd: ${test_name}"
        commit_message+=$'\n\nReviewers: UNKNOWNONE, UNKNOWNTWO'
        git commit -m "${commit_message}"
        git push origin ${branch_name}
    cd -
    run_arcyd

    # update the review branch
    cd dev
        echo goodbye > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 2"
        git push origin ${branch_name}
        git branch -r | grep "origin/${branch_name}"
    cd -
    run_arcyd

    # update the review branch
    cd dev
        echo au reviour > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 3"
        echo adio > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - commit 4"
        git push origin ${branch_name}
        git branch -r | grep "origin/${branch_name}"
    cd -
    run_arcyd

    # find and accept the review
    revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
    run_arcyd

    # make sure the revision is closed and landed
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Closed'
    cd dev
        deleted_prefix='deleted.*'
        git fetch -p 2>&1 | grep "${deleted_prefix}${branch_name}"
    cd -
}

function test_bad_base() {
    test_name='test_bad_base'
    set_branch_name "nonesuch" "${test_name}"

    # create a review branch
    create_review_branch "${branch_name}" "${test_name}"

    run_arcyd

    # find and accept the review
    revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
    run_arcyd

    # make sure the revision is still Accepted
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Accepted'

    # remove the review branch
    cd dev
        git push origin :${branch_name}
    cd -
    run_arcyd
}

function test_self_review() {
    test_name='test_self_review'
    set_branch_name "master" "${test_name}"

    # create a review branch
    cd dev
        git checkout -b ${branch_name} origin/master
        echo hello > ${test_name}
        git add ${test_name}
        commit_message=$(printf "exercise_arcyd: ${test_name}\n\nreviewers: bob")
        git commit -m "${commit_message}"
        git push origin ${branch_name}
    cd -
    run_arcyd

    # find and accept the review
    revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
    run_arcyd

    # make sure the revision is closed and landed
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Closed'
    cd dev
        deleted_prefix='deleted.*'
        git fetch -p 2>&1 | grep "${deleted_prefix}${branch_name}"
    cd -
}

function test_merge_conflict() {
    test_name='test_merge_conflict'
    set_branch_name "master" "${test_name}"

    # create a review branch
    create_review_branch "${branch_name}" "${test_name}"

    run_arcyd

    # create a conflicting change on master
    cd dev
        git checkout master
        git merge --ff-only origin/master
        echo goodbye > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name}: conflicting change"
        git push origin master
        git checkout ${branch_name}
    cd -

    # find and accept the review
    revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
    run_arcyd

    # make sure the revision is 'Needs revision'
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Needs Revision'

    # accept the review again
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}

    # resolve the merge conflict
    cd dev
        git merge -s ours origin/master --no-edit
        git push origin ${branch_name}
    cd -
    run_arcyd

    # make sure the revision is closed and landed
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Closed'
    cd dev
        deleted_prefix='deleted.*'
        git fetch -p 2>&1 | grep "${deleted_prefix}${branch_name}"
    cd -
}

function test_push_error() {
    test_name='test_push_error'
    set_branch_name "master" "${test_name}"

    # create a review branch
    create_review_branch "${branch_name}" "${test_name}"

    run_arcyd

    # prevent writes to origin
    chmod -R u-w origin

    # find and accept the review
    revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
    run_arcyd

    # make sure the revision is 'Needs revision'
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Needs Revision'

    # accept the review again
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}

    # enable writes to origin and try to land again
    chmod -R u+w origin
    run_arcyd

    # make sure the revision is closed and landed
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Closed'
    cd dev
        deleted_prefix='deleted.*'
        git fetch -p 2>&1 | grep "${deleted_prefix}${branch_name}"
    cd -
}

function test_empty_branch() {
    test_name='test_empty_branch'
    set_branch_name "master" "${test_name}"

    # create a review branch
    cd dev
        git checkout -b ${branch_name} origin/master
        git push origin ${branch_name}
    cd -
    run_arcyd

    # find and accept the review
    revisionid=$(${arcyon} query --max-results 1 --format-type ids ${arcyoncreds})
    ${arcyon} comment ${revisionid} --action accept --act-as-user alice ${arcyoncreds}
    run_arcyd

    # make sure the revision is 'Accepted'
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Accepted'

    # update the review branch
    cd dev
        echo hello > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name} - non-empty commit"
        git push origin ${branch_name}
    cd -
    run_arcyd

    # make sure the revision is closed and landed
    ${arcyon} query --ids ${revisionid} ${arcyoncreds} | grep 'Closed'
    cd dev
        deleted_prefix='deleted.*'
        git fetch -p 2>&1 | grep "${deleted_prefix}${branch_name}"
    cd -
}

function test_branch_gc() {
    # gc the review branches
    cd dev
        git checkout master  # we can't remove the current branch, be on master
        git fetch origin refs/arcyd/landed:refs/arcyd/landed
        git branch --merged refs/arcyd/landed | grep -v '*' | xargs git branch -D
    cd -
}

###############################################################################
# run the actual tests
###############################################################################

olddir=$(pwd)
tempdir=$(mktemp -d)
cd ${tempdir}
touch savemail.txt

# set up an install of arcyd
setup_repos
configure_arcyd
run_arcyd

# run through the tests
test_happy_path
test_large_add
test_large_file_small_change
test_unknown_reviewer
test_unknown_user
test_bad_base
test_self_review
test_merge_conflict
test_push_error
test_empty_branch
test_branch_gc

# delete all local working branches for clean slate, reset master to initial commit
(cd dev; git checkout master; git branch | grep -v '\*' | xargs git branch -D)
(cd dev; git checkout master; git rev-list HEAD | tail -n 1 | xargs git reset --hard; git push -f origin master)

# use the r-branch naming scheme
arcyd_branch_awk_string="${r_arcyd_branch_awk_string}"

# run through the tests
test_happy_path
test_large_add
test_large_file_small_change
test_unknown_reviewer
test_unknown_user
test_bad_base
test_self_review
test_merge_conflict
test_push_error
test_empty_branch
test_branch_gc

# display the sent mails
pwd
cat savemail.txt

# display the io activity
cat arcyd/var/log/git-phab-writes.log

# clean up
cd ${olddir}
rm -rf ${tempdir}

trap - EXIT
# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# ------------------------------ END-OF-FILE ----------------------------------
