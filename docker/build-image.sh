#! /usr/bin/env bash
set -euo pipefail
THIS_DIR=$(cd $(dirname $0); pwd -P)
echo ${THIS_DIR}
BUILD_DIR=$(mktemp -d /tmp/temp.XXXXX)
DOCKERFILE=$(readlink -f "$1")

pushd ${BUILD_DIR}
cp -R "${THIS_DIR}/.." .
cp "$DOCKERFILE" Dockerfile
docker build -t "$2" .
popd

rm -rf ${BUILD_DIR}
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
