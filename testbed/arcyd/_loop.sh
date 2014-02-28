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
logger="${olddir}/logerror"
touch savemail.txt
touch logerror.txt

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

# run an http server for Git in the background, for snooping
cd origin
    mv hooks/post-update.sample hooks/post-update
    python -m SimpleHTTPServer 8000 &
    webserver_pid=$!
cd -

mkdir arcyd
cd arcyd

$arcyd init \
    --sleep-secs 1 \
    --sendmail-binary ${mail} \
    --sendmail-type catchmail

$arcyd add-phabricator \
    --name local \
    --instance-uri http://127.0.0.1/api/ \
    --review-url-format 'http://127.0.0.1/D{review}' \
    --arcyd-user phab \
    --arcyd-cert \
xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrvafgzqu\
zl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w6lcseh\
s2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk3lyr3u\
vot7fxrotwpi3ty2b2sa2kvlpf

$arcyd add-repohost \
    --name local_git \
    --repo-url-format '../{}' \
    --repo-snoop-url 'http://localhost:8000/info/refs'

$arcyd add-repo \
    --name local \
    --phabricator-name local \
    --repohost-name local_git \
    --repo-desc local_repo \
    --repo-url origin \
    --arcyd-email 'arcyd@localhost' \
    --admin-email 'local-repo-admin@localhost' \

cd ..

echo 'press enter to stop.'

cd arcyd
    # run arcyd in the background
    ${arcyd} start &
    arcyd_pid=$!
cd ..

# run arcyd instaweb in the background
${arcyd} \
    instaweb \
    --report-file arcyd/var/status/arcyd_status.json \
    --repo-file-dir arcyd/var/status \
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
    touch dev/__kill_poke__
    (cd arcyd; ${arcyd} stop)
    wait $pokeloop_pid

    echo $webserver_pid
    kill $webserver_pid

    # display the sent mails
    pwd
    cat savemail.txt
    cat logerror.txt

    # clean up
    cd ${olddir}
    rm -rf ${tempdir}

    echo finished.
}

trap cleanup EXIT
read
trap - EXIT
cleanup
#------------------------------------------------------------------------------
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
#------------------------------- END-OF-FILE ----------------------------------
