#! /bin/bash
set -eux

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

docker kill phab-mysql || true
docker kill phab-web || true
docker rm phab-mysql || true
docker rm phab-web || true

docker run -d --name phab-mysql -e MYSQL_ALLOW_EMPTY_PASSWORD=yes mysql
docker build -t phabricator ../../docker/phabricator
docker run -d -p 80:80 --name phab-web --link phab-mysql phabricator
docker exec phab-web apt-get install mysql-client -y
docker exec phab-web sh -c 'until mysql --host phab-mysql; do sleep 1; done'
docker exec phab-web /phabricator/instances/dev/phabricator/bin/config set mysql.host phab-mysql
docker exec phab-web mkdir -p /opt/
docker exec phab-web git clone https://github.com/bloomberg/phabricator-tools /opt/phabricator-tools
docker exec phab-web sh -c 'mysql --host phab-mysql < /opt/phabricator-tools/vagrant/puppet/phabricator/files/initial.db'
docker exec phab-web /phabricator/instances/dev/phabricator/bin/storage upgrade -f

# -----------------------------------------------------------------------------
# Copyright (C) 2016 Bloomberg Finance L.P.
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
