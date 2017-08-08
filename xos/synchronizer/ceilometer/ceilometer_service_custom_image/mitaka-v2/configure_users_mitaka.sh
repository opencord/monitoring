
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
export OS_URL=http://localhost:35357/v2.0
#Deleting services:
for i in $(openstack service list -f table -c ID); do openstack service delete $i; done
for i in $(openstack user list -f table -c ID); do openstack user delete $i; done
for i in $(openstack role list -f table -c ID); do openstack role delete $i; done
for i in $(openstack project list -f table -c ID); do openstack project delete $i; done
openstack service create --name keystone --description "OpenStack Identity" identity
openstack endpoint create \
  --publicurl http://localhost:5000/v2.0 \
  --internalurl http://localhost:5000/v2.0 \
  --adminurl http://localhost:35357/v2.0 \
  --region RegionOne \
  identity
openstack project create --description "Admin Project" admin
openstack user create admin --password password --email admin@cord.com
openstack role create admin
openstack role add --project admin --user admin admin
openstack project create --description "Service Project" service
openstack project create --description "Demo Project" demo
openstack user create demo --password password --email demo@cord.com
openstack role create user
openstack role add --project demo --user demo user
openstack user create ceilometer --password password --email ceilometer@cord.com
openstack role add --project service --user ceilometer admin
openstack service create --name ceilometer --description "Telemetry" metering
openstack endpoint create \
  --publicurl http://localhost:8777 \
  --internalurl http://localhost:8777 \
  --adminurl http://localhost:8777 \
  --region RegionOne \
  metering
openstack user list
openstack role list
openstack project list
openstack service list
openstack endpoint list
