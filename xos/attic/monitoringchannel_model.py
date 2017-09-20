
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


sync_attributes = ("private_ip", "private_mac",
                   "ceilometer_ip", "ceilometer_mac",
                   "nat_ip", "nat_mac", "ceilometer_port",)

default_attributes = {}
def __init__(self, *args, **kwargs):
    ceilometer_services = CeilometerService.get_service_objects().all()
    if ceilometer_services:
        self._meta.get_field("provider_service").default = ceilometer_services[0].id
    super(MonitoringChannel, self).__init__(*args, **kwargs)
    self.set_attribute("use_same_instance_for_multiple_tenants", True)

def can_update(self, user):
    #Allow creation of this model instances for non-admin users also
    return True

def __xos_save_base(self, *args, **kwargs):
    if not self.creator:
        if not getattr(self, "caller", None):
            # caller must be set when creating a monitoring channel since it creates a slice
            raise XOSProgrammingError("MonitoringChannel's self.caller was not set")
        self.creator = self.caller
        if not self.creator:
            raise XOSProgrammingError("MonitoringChannel's self.creator was not set")

    if self.pk is None:
        #Allow only one monitoring channel per user
        channel_count = sum ( [1 for channel in MonitoringChannel.get_tenant_objects().all() if (channel.creator == self.creator)] )
        if channel_count > 0:
            raise XOSValidationError("Already %s channels exist for user Can only create max 1 MonitoringChannel instance per user" % str(channel_count))

    model_policy_monitoring_channel(self.pk)
    return False

def delete(self, *args, **kwargs):
    self.cleanup_container()
    super(MonitoringChannel, self).delete(*args, **kwargs)

@property
def addresses(self):
    if (not self.id) or (not self.instance):
        return {}

    addresses = {}
    for ns in self.instance.ports.all():
        if "private" in ns.network.name.lower():
            addresses["private"] = (ns.ip, ns.mac)
        elif ("nat" in ns.network.name.lower()) or ("management" in ns.network.name.lower()):
            addresses["nat"] = (ns.ip, ns.mac)
        #TODO: Do we need this client_access_network. Revisit in VTN context
        #elif "ceilometer_client_access" in ns.network.labels.lower():
        #    addresses["ceilometer"] = (ns.ip, ns.mac)
    return addresses

@property
def nat_ip(self):
    return self.addresses.get("nat", (None, None))[0]

@property
def nat_mac(self):
    return self.addresses.get("nat", (None, None))[1]

@property
def private_ip(self):
    return self.addresses.get("private", (None, None))[0]

@property
def private_mac(self):
    return self.addresses.get("private", (None, None))[1]

@property
def ceilometer_ip(self):
    return self.addresses.get("ceilometer", (None, None))[0]

@property
def ceilometer_mac(self):
    return self.addresses.get("ceilometer", (None, None))[1]

@property
def site_tenant_list(self):
    tenant_ids = Set()
    for sp in SitePrivilege.objects.filter(user=self.creator):
        site = sp.site
        for cs in site.controllersite.all():
           if cs.tenant_id:
               tenant_ids.add(cs.tenant_id)
    return tenant_ids

@property
def slice_tenant_list(self):
    tenant_ids = Set()
    for sp in SlicePrivilege.objects.filter(user=self.creator):
        slice = sp.slice
        for cs in slice.controllerslices.all():
           if cs.tenant_id:
               tenant_ids.add(cs.tenant_id)
    for slice in Slice.objects.filter(creator=self.creator):
        for cs in slice.controllerslices.all():
            if cs.tenant_id:
                tenant_ids.add(cs.tenant_id)
    if self.creator.is_admin:
        #TODO: Ceilometer publishes the SDN meters without associating to any tenant IDs.
        #For now, ceilometer code is changed to pusblish all such meters with tenant
        #id as "default_admin_tenant". Here add that default tenant as authroized tenant_id
        #for all admin users. 
        tenant_ids.add("default_admin_tenant")
    return tenant_ids

@property
def tenant_list(self):
    return self.slice_tenant_list | self.site_tenant_list

@property
def tenant_list_str(self):
    return ", ".join(self.tenant_list)

@property
def ceilometer_port(self):
    # TODO: Find a better logic to choose unique ceilometer port number for each instance 
    if not self.id:
        return None
    return 8888+self.id

@property
def ssh_proxy_tunnel(self):
    return self.get_attribute("ssh_proxy_tunnel", False)

@ssh_proxy_tunnel.setter
def ssh_proxy_tunnel(self, value):
    self.set_attribute("ssh_proxy_tunnel", value)

@property
def ssh_tunnel_port(self):
    return self.get_attribute("ssh_tunnel_port")

@ssh_tunnel_port.setter
def ssh_tunnel_port(self, value):
    self.set_attribute("ssh_tunnel_port", value)

@property
def ssh_tunnel_ip(self):
    return self.get_attribute("ssh_tunnel_ip")

@ssh_tunnel_ip.setter
def ssh_tunnel_ip(self, value):
    self.set_attribute("ssh_tunnel_ip", value)

@property
def ceilometer_url(self):
    if self.private_ip and self.ceilometer_port:
        return "http://" + self.private_ip + ":" + str(self.ceilometer_port) + "/"
    else:
        return None

@property
def ceilometer_ssh_proxy_url(self):
    if self.ssh_proxy_tunnel:
        if self.ssh_tunnel_ip and self.ssh_tunnel_port:
            return "http://" + self.ssh_tunnel_ip + ":" + str(self.ssh_tunnel_port) + "/"
        else:
            return None
    else:
        return None

@property
def kafka_url(self):
    ceilometer_services = CeilometerService.get_service_objects().all()
    if not ceilometer_services:
        return None
    return ceilometer_services[0].kafka_url
