
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


sync_attributes = ("listening_endpoint", )

default_attributes = {}
def __init__(self, *args, **kwargs):
    sflow_services = SFlowService.get_service_objects().all()
    if sflow_services:
        self._meta.get_field("provider_service").default = sflow_services[0].id
    super(SFlowTenant, self).__init__(*args, **kwargs)

@property
def creator(self):
    from core.models import User
    if getattr(self, "cached_creator", None):
        return self.cached_creator
    creator_id=self.get_attribute("creator_id")
    if not creator_id:
        return None
    users=User.objects.filter(id=creator_id)
    if not users:
        return None
    user=users[0]
    self.cached_creator = users[0]
    return user

@creator.setter
def creator(self, value):
    if value:
        value = value.id
    if (value != self.get_attribute("creator_id", None)):
        self.cached_creator=None
    self.set_attribute("creator_id", value)

@property
def listening_endpoint(self):
    return self.get_attribute("listening_endpoint", None)

@listening_endpoint.setter
def listening_endpoint(self, value):
    if urlparse(value).scheme != 'udp':
        raise XOSProgrammingError("SFlowTenant: Only UDP listening endpoint URLs are accepted...valid syntax is: udp://ip:port")
    self.set_attribute("listening_endpoint", value)

def __xos_save_base(self, *args, **kwargs):
    if not self.creator:
        if not getattr(self, "caller", None):
            # caller must be set when creating a SFlow tenant since it creates a slice
            raise XOSProgrammingError("SFlowTenant's self.caller was not set")
        self.creator = self.caller
        if not self.creator:
            raise XOSProgrammingError("SFlowTenant's self.creator was not set")

    if not self.listening_endpoint:
        raise XOSProgrammingError("SFlowTenant's self.listening_endpoint was not set")

    if self.pk is None:
        #Allow only one sflow channel per user and listening_endpoint
        channel_count = sum ( [1 for channel in SFlowTenant.get_tenant_objects().all() if ((channel.creator == self.creator) and (channel.listening_endpoint == self.listening_endpoint))] )
        if channel_count > 0:
            raise XOSValidationError("Already %s sflow channels exist for user Can only create max 1 tenant per user and listening endpoint" % str(channel_count))

    return False

def delete(self, *args, **kwargs):
    super(MonitoringChannel, self).delete(*args, **kwargs)

@property
def authorized_resource_list(self):
    return ['all']

@property
def authorized_resource_list_str(self):
    return ", ".join(self.authorized_resource_list)
