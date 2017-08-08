
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


STARTUP_PATH="/home/ubuntu/monitoring/xos/synchronizer/ceilometer/ceilometer_service_custom_image/startup-scripts"
IP=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep "10.0.3")
#IP=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep "10.11.10")
echo $IP
sudo rabbitmqctl add_user openstack "password"
sudo rabbitmqctl set_permissions openstack ".*" ".*" ".*"
python $STARTUP_PATH/update-endpoints.py --username root --password password --host localhost --endpoint $IP --endpoint-type public
python $STARTUP_PATH/update-endpoints.py --username root --password password --host localhost --endpoint $IP --endpoint-type admin
