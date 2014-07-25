trap "echo 'FAILED!'; exit 1" ERR
#set -x
set -eu
set -o pipefail

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

conduitproxy="$(pwd)/../../proto/conduit-proxy"
arcyon="$(pwd)/../../bin/arcyon"

tempdir=$(mktemp -d)
olddir=$(pwd)
cd ${tempdir}

phaburi="http://127.0.0.1"
phabuser='phab'
phabcert=xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrv\
afgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w\
6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk\
3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

proxysecret=squirrel

# openssl genrsa > privkey.pem
# openssl req -new -x509 -key privkey.pem -out mycert.pem -days 1095\
#     -subj "/C=US/ST=Oregon/L=Portland/O=IT/CN=127.0.0.1"
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes\
    -subj "/C=US/ST=Oregon/L=Portland/O=IT/CN=127.0.0.1"

$conduitproxy\
    --uri ${phaburi}\
    --user ${phabuser}\
    --cert ${phabcert}\
    --sslcert server.pem\
    --secret ${proxysecret}\
    --port 8118\
    &
conduitproxypid=$!


function cleanup() {
    set +e

    kill $conduitproxypid

    # clean up
    cd ${olddir}
    rm -rf ${tempdir}
}

trap "echo 'FAILED!'; cleanup; exit 1" ERR

$conduitproxy -h

conduitproxyuri='https://127.0.0.1:8118'

$arcyon query\
    --uri $conduitproxyuri\
    --user blerg\
    --cert ${proxysecret}\
    --max-results 1

$arcyon query\
    --uri $conduitproxyuri\
    --user werg\
    --cert ${proxysecret}\
    --max-results 1

echo
cat conduit-proxy.log
echo

trap - ERR
cleanup
echo OK
# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
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
