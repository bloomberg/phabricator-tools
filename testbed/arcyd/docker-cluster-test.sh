#! /bin/bash
set -eux

# NOTE: This script expects you to have phab running in a local container
# called 'phab-web', serving http. The test users are expected to be installed,
# as found in phldef_conduit.py and set up with puppet manifest in
# phabricator-tools.
#
# You can achieve this by simply running:
#
#   $ ./testbed/docker-phabricator/run-docker-phab-web-mysql.sh
#
# It will run the necessary containers for you.

# NOTE: This script expects you to have built the 'gitdaemon' and 'gituser'
# images already. It will build the arcyd image for you.

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

docker kill arcydclustertest-git || true
docker kill arcydclustertest-arcyd || true
docker kill arcydclustertest-arcyd2 || true
docker kill arcydclustertest-consulserver || true
docker rm arcydclustertest-git || true
docker rm arcydclustertest-arcyd || true
docker rm arcydclustertest-arcyd2 || true
docker rm arcydclustertest-consulserver || true

docker run -d --name arcydclustertest-consulserver gliderlabs/consul-server -bootstrap-expect 1
CONSUL_SERVER_IP=$(docker inspect arcydclustertest-consulserver | python -c 'import json; import sys; print json.load(sys.stdin)[0]["NetworkSettings"]["IPAddress"]')

# wait for consul server to be ready
while ! docker exec arcydclustertest-consulserver consul info | grep 'leader = true'; do sleep 1; done

docker build -t arcydclustertest-gituser ../../docker/gituser/
docker build -t arcydclustertest-gitdaemon ../../docker/gitdaemon/
../../docker/build-image.sh ../../docker/arcyd-cluster/arcyd-dockerfile arcyd-cluster

docker run -d --name arcydclustertest-git arcydclustertest-gitdaemon arcyd testrepo
docker run -d --name arcydclustertest-arcyd --link arcydclustertest-git:git --link phab-web arcyd-cluster git://git/arcyd "${CONSUL_SERVER_IP}"

# wait for arcyd container to be ready
while ! docker exec arcydclustertest-arcyd arcyd-do list-repos 2> /dev/null; do sleep 1; done

docker exec arcydclustertest-arcyd arcyd-do add-repohost --name mygit

phaburi="http://phab-web"
arcyduser='phab'
arcydcert=xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrv\
afgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w\
6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk\
3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

docker exec arcydclustertest-arcyd arcyd-do add-phabricator \
    --name phabweb \
    --instance-uri "$phaburi/api/" \
    --review-url-format '$phaburi/D{review}' \
    --admin-emails 'local-phab-admin@localhost' \
    --arcyd-user "$arcyduser" \
    --arcyd-cert "$arcydcert"

docker run --rm --link arcydclustertest-git:git -i arcydclustertest-gituser <<EOF
    mkdir data
    cd data
    git clone git://git/testrepo
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

docker exec arcydclustertest-arcyd arcyd-do add-repo phabweb mygit git://git/testrepo --name testrepo
docker exec arcydclustertest-arcyd sh -c 'cd /var/arcyd; git push origin master;'
docker exec arcydclustertest-arcyd arcyd-do reload

docker run -d --name arcydclustertest-arcyd2 --link arcydclustertest-git:git --link phab-web arcyd-cluster git://git/arcyd "${CONSUL_SERVER_IP}"

# let some stuff happen
sleep 5

echo ----- arcyd 1 -----
docker logs arcydclustertest-arcyd
echo ----- arcyd 2 -----
docker logs arcydclustertest-arcyd2

docker kill arcydclustertest-git
docker kill arcydclustertest-arcyd
docker kill arcydclustertest-arcyd2
docker kill arcydclustertest-consulserver
docker rm arcydclustertest-git
docker rm arcydclustertest-arcyd
docker rm arcydclustertest-arcyd2
docker rm arcydclustertest-consulserver

# -----------------------------------------------------------------------------
# Copyright (C) 2015-2016 Bloomberg Finance L.P.
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
