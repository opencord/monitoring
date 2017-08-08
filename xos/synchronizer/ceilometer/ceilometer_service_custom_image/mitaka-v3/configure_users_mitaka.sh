
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


set -x
export OS_TOKEN=ADMIN_TOKEN
export OS_URL=http://localhost:35357/v3
export OS_IDENTITY_API_VERSION=3
#Deleting services:
for i in $(openstack service list -f table -c ID); do openstack service delete $i; done
for i in $(openstack user list -f table -c ID); do openstack user delete $i; done
for i in $(openstack role list -f table -c ID); do openstack role delete $i; done
for i in $(openstack project list -f table -c ID); do openstack project delete $i; done
openstack service create --name keystone --description "OpenStack Identity" identity
openstack endpoint create --region RegionOne identity public http://localhost:5000/v3
openstack endpoint create --region RegionOne identity internal http://localhost:5000/v3
openstack endpoint create --region RegionOne identity admin http://localhost:35357/v3

openstack domain create --description "Default Domain" default

openstack project create --domain default --description "Admin Project" admin

openstack user create --domain default --password password admin

openstack role create admin
openstack role add --project admin --user admin admin

openstack project create --domain default --description "Service Project" service
openstack project create --domain default --description "Demo Project" demo

openstack user create --domain default --password password demo
openstack role create user
openstack role add --project demo --user demo user

openstack user create --domain default --password password ceilometer
openstack role add --project service --user ceilometer admin

openstack service create --name ceilometer --description "Telemetry" metering
openstack endpoint create --region RegionOne   metering public http://localhost:8777
openstack endpoint create --region RegionOne   metering internal http://localhost:8777
openstack endpoint create --region RegionOne   metering admin http://localhost:8777

openstack user list
openstack service list
