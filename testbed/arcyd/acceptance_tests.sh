###############################################################################
# acceptance tests for Arcyd, aimed at a more comprehensive coverage at the
# cost of a longer running time.
###############################################################################

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

tempdir=$(mktemp -d)
olddir=$(pwd)
cd ${tempdir}

mail="${olddir}/savemail"
touch savemail.txt

function setup_repos() {
    mkdir origin
    cd origin
    git init --bare
    cd ..

    git clone origin dev
    cd dev
    git config user.name 'Bob User'
    git config user.email 'bob@server.test'
    touch README
    git add README
    git commit -m 'intial commit'
    git push origin master
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
    ${arcyd} \
        process-repos \
        --sys-admin-emails admin@server.test \
        --sendmail-binary ${mail} \
        --sendmail-type catchmail \
        --repo-configs @repo_arcyd.cfg \
        --status-path arcyd_status.json \
        --sleep-secs 0 \
        --no-loop
    echo $?

    ${arcyd} \
        arcyd-status-html \
        arcyd_status.json \
        https://server.test/arcyd > /dev/null
    echo $?

    ${arcyd} \
        repo-status-html \
        touches/repo_origin.try \
        touches/repo_origin.ok > /dev/null
    echo $?
}

function test_happy_path() {
    test_name='test_happy_path'
    branch_name="arcyd-review/${test_name}/master"

    # create a review branch
    cd dev
        git checkout -b ${branch_name} origin/master
        echo hello > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name}"
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
    branch_name="arcyd-review/${test_name}/master"

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

function test_bad_base() {
    test_name='test_unknown_user'
    branch_name="arcyd-review/${test_name}/nonesuch"

    # create a review branch
    cd dev
        git checkout -b ${branch_name} origin/master
        echo hello > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name}"
        git push origin ${branch_name}
    cd -
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
    branch_name="arcyd-review/${test_name}/master"

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
    branch_name="arcyd-review/${test_name}/master"

    # create a review branch
    cd dev
        git checkout -b ${branch_name} origin/master
        echo hello > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name}"
        git push origin ${branch_name}
    cd -
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
    branch_name="arcyd-review/${test_name}/master"

    # create a review branch
    cd dev
        git checkout -b ${branch_name} origin/master
        echo hello > ${test_name}
        git add ${test_name}
        git commit -m "exercise_arcyd: ${test_name}"
        git push origin ${branch_name}
    cd -
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
    branch_name="arcyd-review/${test_name}/master"

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
        ${barc} gc --force --update
    cd -
}

###############################################################################
# run the actual tests
###############################################################################

# set up an install of arcyd
setup_repos
configure_arcyd
run_arcyd

# run through the tests
test_happy_path
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

# clean up
cd ${olddir}
rm -rf ${tempdir}

trap - EXIT
