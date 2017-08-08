
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
PUB_SUB_PATH=/home/ubuntu/monitoring/xos/synchronizer/ceilometer/ceilometer_pub_sub
echo $PWD
cd $PUB_SUB_PATH
sleep 5
chmod +x sub_main.py
nohup ./sub_main.py &
echo $PWD
cd -
echo $PWD
