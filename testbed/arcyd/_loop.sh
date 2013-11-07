###############################################################################
# looping test for Arcyd, aimed at exercising the whole cycle
###############################################################################

if [ $# -ne 1 ]
then
    echo usage: _loop.sh PATH_TO_ARCYD_FROM_SCRIPT
    echo example: _loop.sh ../../proto/arcyd
    exit
fi

arcyd="$1"

set +x
set -e
trap "echo FAILED!; exit 1" EXIT


# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

pokeloop="$(pwd)/poke_loop.sh"
arcyon="$(pwd)/../../bin/arcyon"

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
echo touches/repo_arcyd.cfg.try >> repo_arcyd.cfg
echo --ok-touch-path >> repo_arcyd.cfg
echo touches/repo_arcyd.cfg.ok >> repo_arcyd.cfg
echo --review-url-format >> repo_arcyd.cfg
echo 'http://127.0.0.1/D{review}' >> repo_arcyd.cfg
# echo --branch-url-format >> repo_arcyd.cfg
# echo 'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}' >> repo_arcyd.cfg
echo --repo-snoop-url >> repo_arcyd.cfg
echo 'http://localhost:8000/info/refs' >> repo_arcyd.cfg

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

echo 'press enter to stop.'

# run an http server for Git in the background, for snooping
cd origin
    mv hooks/post-update.sample hooks/post-update
    python -m SimpleHTTPServer 8000 &
    webserver_pid=$!
cd -

# run arcyd in the background
${arcyd} \
    process-repos \
    --sys-admin-emails admin@server.test \
    --sendmail-binary ${mail} \
    --sendmail-type catchmail \
    --repo-configs @repo_arcyd.cfg \
    --status-path arcyd_status.json \
    --kill-file killfile \
    --sleep-secs 1 \
&
arcyd_pid=$!

# run arcyd instaweb in the background
${arcyd} \
    instaweb \
    --report-file arcyd_status.json \
    --repo-file-dir touches \
    --port 8001 \
&
instaweb_pid=$!

# run poke_loop.sh in the background
cd dev
    ${pokeloop} > /dev/null &
    pokeloop_pid=$!
cd -

function cleanup() {

    set +e

    echo $instaweb_pid
    kill $instaweb_pid
    wait $instaweb_pid

    # kill arycd and poke_loop
    touch killfile
    touch dev/__kill_poke__
    wait $arcyd_pid
    wait $pokeloop_pid

    echo $webserver_pid
    kill $webserver_pid

    # display the sent mails
    pwd
    cat savemail.txt

    # clean up
    cd ${olddir}
    rm -rf ${tempdir}

    echo finished.
}

trap cleanup EXIT
read
trap - EXIT
cleanup
