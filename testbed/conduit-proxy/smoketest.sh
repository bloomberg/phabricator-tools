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
