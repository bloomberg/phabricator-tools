#! /bin/bash
set -eux

# NOTE: This script expects you to have phab running in a local container
# called 'phab-web', serving http. The test users are expected to be installed,
# as found in phldef_conduit.py and set up with puppet manifest in
# phabricator-tools.

# NOTE: This script expects you to have built the 'gitdaemon' and 'gituser'
# images already. It will build the arcyd image for you.

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

cd ../../docker/arcyd

docker kill arcydtest-git || true
docker kill arcydtest-arcyd || true
docker rm arcydtest-git || true
docker rm arcydtest-arcyd || true

docker run -d --name arcydtest-git gitdaemon arcyd testrepo
../build-image.sh arcyd-dockerfile arcyd
docker run -d --name arcydtest-arcyd arcyd git://arcydtest-git/arcyd

# wait for arcyd container to be ready
while ! docker exec arcydtest-arcyd arcyd-do list-repos 2> /dev/null; do sleep 1; done

docker exec arcydtest-arcyd arcyd-do add-repohost --name mygit

phaburi="http://phab-web"
arcyduser='phab'
arcydcert=xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrv\
afgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w\
6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk\
3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

docker exec arcydtest-arcyd arcyd-do add-phabricator \
    --name phabweb \
    --instance-uri "$phaburi/api/" \
    --review-url-format '$phaburi/D{review}' \
    --admin-emails 'local-phab-admin@localhost' \
    --arcyd-user "$arcyduser" \
    --arcyd-cert "$arcydcert"

docker run --rm -i gituser <<EOF
    mkdir data
    cd data
    git clone git://arcydtest-git/testrepo
    cd testrepo
    git config user.email alice@server.test
    git config user.name alice
    touch README
    git add README
    git commit -m README
    git push origin master
    git checkout -b r/master/hello
    echo Hello > README
    git commit -am hello
    git push origin r/master/hello
EOF

docker exec arcydtest-arcyd arcyd-do add-repo phabweb mygit git://arcydtest-git/testrepo --name testrepo
docker exec arcydtest-arcyd arcyd-do reload
docker logs arcydtest-arcyd

sleep 5
docker exec arcydtest-arcyd cat var/arcyd/var/log/info

docker kill arcydtest-git
docker kill arcydtest-arcyd
docker rm arcydtest-git
docker rm arcydtest-arcyd
# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
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
