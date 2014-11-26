###############################################################################
# looping test for Arcyd, aimed at exercising the whole cycle
###############################################################################

if [ $# -ne 1 ]
then
    echo usage: _loop.sh PATH_TO_ARCYD_FROM_SCRIPT
    echo example: _loop.sh ../../proto/arcyd
    exit
fi

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

arcyd="$1"
safe_arcyd="$(pwd)/../../proto/arcyd"

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

$safe_arcyd init \
    --sleep-secs 1 \
    --arcyd-email 'arcyd@localhost' \
    --sendmail-binary ${mail} \
    --sendmail-type catchmail

$safe_arcyd add-phabricator \
    --name localhost \
    --instance-uri http://127.0.0.1/api/ \
    --review-url-format 'http://127.0.0.1/D{review}' \
    --arcyd-user phab \
    --arcyd-cert \
xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrvafgzqu\
zl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w6lcseh\
s2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk3lyr3u\
vot7fxrotwpi3ty2b2sa2kvlpf

$safe_arcyd add-repohost \
    --name fs \
    --repo-url-format '../{}' \
    --admin-email 'local-repo-admin@localhost' \
    --repo-snoop-url 'http://localhost:8000/info/refs'

$safe_arcyd add-repo localhost fs origin

cd ..

echo 'press enter to stop.'

cd arcyd
    # run arcyd in the background
    ${arcyd} start
cd ..

# run poke_loop.sh in the background
cd dev
    ${pokeloop} > /dev/null &
    pokeloop_pid=$!
cd -

function cleanup() {

    set +e

    # kill arcyd and poke_loop
    touch dev/__kill_poke__
    (cd arcyd; ${arcyd} stop)
    wait $pokeloop_pid

    echo $webserver_pid
    kill $webserver_pid

    # display the sent mails and other messages
    pwd
    cat savemail.txt
    cat logerror.txt
    cat arcyd/var/log/info

    # clean up
    cd ${olddir}
    rm -rf ${tempdir}

    echo finished.
}

trap cleanup EXIT
read
trap - EXIT
cleanup
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
