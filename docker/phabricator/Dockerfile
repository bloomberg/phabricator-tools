FROM ubuntu:14.04
MAINTAINER Angelos Evripiotis <jevripiotis@bloomberg.net>
EXPOSE 80
RUN apt-get update && apt-get install -y \
    git \
    php5 \
    php5-mysql \
    php5-gd \
    php5-dev \
    php5-curl \
    php-apc \
    php5-cli \
    apache2
RUN mkdir -p /phabricator/instances/dev
RUN git clone https://github.com/phacility/phabricator /phabricator/instances/dev/phabricator
RUN git clone https://github.com/phacility/libphutil /phabricator/instances/dev/libphutil
RUN git clone https://github.com/phacility/arcanist /phabricator/instances/dev/arcanist
RUN git -C /phabricator/instances/dev/phabricator reset --hard d13a3225634c47cf2e55b94199a0f2aba37aa293
RUN git -C /phabricator/instances/dev/libphutil reset --hard 0b9f193303dfae4f9204d8f577e2bd45acd4963f
RUN git -C /phabricator/instances/dev/arcanist reset --hard 6270dd0de5073931f3c3e75ab77f0f1d5fa77eef
COPY phab.conf /etc/apache2/sites-available/phab.conf
RUN ln -s /etc/apache2/sites-available/phab.conf /etc/apache2/sites-enabled/phab.conf
RUN rm /etc/apache2/sites-enabled/000-default.conf
RUN /usr/sbin/a2enmod rewrite
CMD /usr/sbin/apache2ctl -D FOREGROUND
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
