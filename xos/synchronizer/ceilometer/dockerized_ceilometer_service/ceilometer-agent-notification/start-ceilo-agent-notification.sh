
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#!/bin/sh

if [ ! -z "$RABBIT_TRANSPORT_URL" ]; then
   sed -r -i "s,[#]*(transport_url) = (.*),\1 = $RABBIT_TRANSPORT_URL,g" /etc/ceilometer/ceilometer.conf
fi
if [ ! -z "$RABBIT_HOST" ]; then
   sed -r -i "s/[#]*(rabbit_host) = (.*)/\1 = $RABBIT_HOST/g" /etc/ceilometer/ceilometer.conf
fi
if [ ! -z "$RABBIT_USER" ]; then
   sed -r -i "s/[#]*(rabbit_userid) = (.*)/\1 = $RABBIT_USER/g" /etc/ceilometer/ceilometer.conf
fi
if [ ! -z "$RABBIT_PASS" ]; then
   sed -r -i "s/[#]*(rabbit_password) = (.*)/\1 = $RABBIT_PASS/g" /etc/ceilometer/ceilometer.conf
fi

#Run ceilometer-agent-notification
/usr/local/bin/ceilometer-agent-notification
