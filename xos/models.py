
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


from django.db import models
from django.core.validators import URLValidator
from core.models import Service, XOSBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, ServiceDependency, ServiceMonitoringAgentInfo
from core.models.xosbase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
import traceback
from xos.exceptions import *
from core.models import SlicePrivilege, SitePrivilege
from sets import Set
from urlparse import urlparse

CEILOMETER_KIND = "ceilometer"
#Ensure the length of name for 'kind' attribute is below 30
CEILOMETER_PUBLISH_TENANT_KIND = "ceilo-publish-tenant"
CEILOMETER_PUBLISH_TENANT_OS_KIND = "ceilo-os-publish-tenant"
CEILOMETER_PUBLISH_TENANT_ONOS_KIND = "ceilo-onos-publish-tenant"
CEILOMETER_PUBLISH_TENANT_USER_KIND = "ceilo-user-publish-tenant"

class CeilometerService(Service):
    KIND = CEILOMETER_KIND
    LOOK_FOR_IMAGES=[ "ceilometer-service-trusty-server-multi-nic",
                    ]

    sync_attributes = ("private_ip", "private_mac",
                       "nat_ip", "nat_mac", "ceilometer_enable_pub_sub")
    class Meta:
        app_label = "monitoring"
        verbose_name = "Ceilometer Service"
        proxy = True

    def get_instance(self):
        for slice in self.slices.all():
             for instance in slice.instances.all():
                 if instance.image.name in self.LOOK_FOR_IMAGES:
                     return instance
        return None

    @property
    def addresses(self):
        if (not self.id) or (not self.get_instance()):
            return {}

        addresses = {}
        for ns in self.get_instance().ports.all():
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

    def get_controller(self):
        if not self.slices.count:
            raise XOSConfigurationError("The service has no slices")
        cslice = self.slices.all()[0].controllerslices.all()[0]
        controller = cslice.controller
        if not controller:
            raise XOSConfigurationError("The service slice has no controller")
        return controller

    @property
    def ceilometer_pub_sub_url(self):
        if not self.get_instance():
            return self.get_attribute("ceilometer_pub_sub_url", None)
        if not self.private_ip:
            return None
        return "http://" + self.private_ip + ":4455/"

    @ceilometer_pub_sub_url.setter
    def ceilometer_pub_sub_url(self, value):
        self.set_attribute("ceilometer_pub_sub_url", value)

    @property
    def ceilometer_enable_pub_sub(self):
        return self.get_attribute("ceilometer_enable_pub_sub", False)

    @ceilometer_enable_pub_sub.setter
    def ceilometer_enable_pub_sub(self, value):
        self.set_attribute("ceilometer_enable_pub_sub", value)

    @property
    def ceilometer_auth_url(self):
        #FIXME: Crude way to determine if monitoring service is getting deployed with its own ceilometer+keystone 
        if not self.get_instance():
            return self.get_controller().auth_url
        if not self.private_ip:
            return None
        return "http://" + self.private_ip + ":5000/v2.0"

    @property
    def ceilometer_admin_user(self):
        if not self.get_instance():
            return self.get_controller().admin_user
        return 'admin'

    @property
    def ceilometer_admin_password(self):
        if not self.get_instance():
            return self.get_controller().admin_password
        return 'password'

    @property
    def ceilometer_admin_tenant(self):
        if not self.get_instance():
            return self.get_controller().admin_tenant
        return 'admin'

    @property
    def ceilometer_rabbit_compute_node(self):
        if not self.get_instance():
            return None
        return self.get_instance().node.name

    @property
    def ceilometer_rabbit_host(self):
        if not self.get_instance():
            return None
        return self.nat_ip

    @property
    def ceilometer_rabbit_user(self):
        if not self.get_instance():
            return None
        return 'openstack'

    @property
    def ceilometer_rabbit_password(self):
        if not self.get_instance():
            return None
        return 'password'

    @property
    def ceilometer_rabbit_uri(self):
        if not self.get_instance():
            return None
        if not self.private_ip:
            return None
        return 'rabbit://openstack:password@' + self.private_ip + ':5672'

    @property
    def kafka_url(self):
        if not self.get_instance():
            return None
        if not self.private_ip:
            return None
        return 'kafka://' + self.private_ip + ':9092'

    def delete(self, *args, **kwargs):
        instance = self.get_instance()
        if instance:
            instance.delete()
        super(CeilometerService, self).delete(*args, **kwargs)


class MonitoringChannel(TenantWithContainer):   # aka 'CeilometerTenant'
    class Meta:
        app_label = "monitoring"
        proxy = True

    KIND = CEILOMETER_KIND
    LOOK_FOR_IMAGES=[ #"trusty-server-multi-nic-docker", # CloudLab
                      "ceilometer-trusty-server-multi-nic",
                      #"trusty-server-multi-nic",
                    ]


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

    def save(self, *args, **kwargs):
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

        super(MonitoringChannel, self).save(*args, **kwargs)
        model_policy_monitoring_channel(self.pk)

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


def model_policy_monitoring_channel(pk):
    # TODO: this should be made in to a real model_policy
    with transaction.atomic():
        mc = MonitoringChannel.objects.select_for_update().filter(pk=pk)
        if not mc:
            return
        mc = mc[0]
        mc.manage_container()

#@receiver(models.signals.post_delete, sender=MonitoringChannel)
#def cleanup_monitoring_channel(sender, o, *args, **kwargs):
#     #o.cleanup_container()
#     #Temporary change only, remove the below code after testing
#     if o.instance:
#         o.instance.delete()
#         o.instance = None

class MonitoringPublisher(Tenant):
    class Meta:
        app_label = "monitoring"
        proxy = True

    KIND = CEILOMETER_PUBLISH_TENANT_KIND

    default_attributes = {}
    def __init__(self, *args, **kwargs):
        ceilometer_services = CeilometerService.get_service_objects().all()
        if ceilometer_services:
            self._meta.get_field("provider_service").default = ceilometer_services[0].id
        super(MonitoringPublisher, self).__init__(*args, **kwargs)

    def can_update(self, user):
        #Allow creation of this model instances for non-admin users also
        return True

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

class OpenStackServiceMonitoringPublisher(MonitoringPublisher):
    class Meta:
        app_label = "monitoring"
        proxy = True

    KIND = CEILOMETER_PUBLISH_TENANT_OS_KIND

    def __init__(self, *args, **kwargs):
        super(OpenStackServiceMonitoringPublisher, self).__init__(*args, **kwargs)

    def can_update(self, user):
        #Don't allow creation of this model instances for non-admin users also
        return False

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a monitoring channel since it creates a slice
                raise XOSProgrammingError("OpenStackServiceMonitoringPublisher's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("OpenStackServiceMonitoringPublisher's self.creator was not set")

        if self.pk is None:
            #Allow only one openstack monitoring publisher per admin user
            publisher_count = sum ( [1 for ospublisher in OpenStackServiceMonitoringPublisher.get_tenant_objects().all() if (ospublisher.creator == self.creator)] )
            if publisher_count > 0:
                raise XOSValidationError("Already %s openstack publishers exist for user Can only create max 1 OpenStackServiceMonitoringPublisher instance per user" % str(publisher_count))

        super(OpenStackServiceMonitoringPublisher, self).save(*args, **kwargs)

class ONOSServiceMonitoringPublisher(MonitoringPublisher):
    class Meta:
        app_label = "monitoring"
        proxy = True

    KIND = CEILOMETER_PUBLISH_TENANT_ONOS_KIND

    def __init__(self, *args, **kwargs):
        super(ONOSServiceMonitoringPublisher, self).__init__(*args, **kwargs)

    def can_update(self, user):
        #Don't allow creation of this model instances for non-admin users also
        return False

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a monitoring channel since it creates a slice
                raise XOSProgrammingError("ONOSServiceMonitoringPublisher's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("ONOSServiceMonitoringPublisher's self.creator was not set")

        if self.pk is None:
            #Allow only one openstack monitoring publisher per admin user
            publisher_count = sum ( [1 for onospublisher in ONOSServiceMonitoringPublisher.get_tenant_objects().all() if (onospublisher.creator == self.creator)] )
            if publisher_count > 0:
                raise XOSValidationError("Already %s openstack publishers exist for user Can only create max 1 ONOSServiceMonitoringPublisher instance per user" % str(publisher_count))

        super(ONOSServiceMonitoringPublisher, self).save(*args, **kwargs)

class UserServiceMonitoringPublisher(MonitoringPublisher):
    class Meta:
        app_label = "monitoring"
        proxy = True

    KIND = CEILOMETER_PUBLISH_TENANT_USER_KIND

    def __init__(self, *args, **kwargs):
        self.cached_target_service = None
        self.cached_tenancy_from_target_service = None
        self.cached_service_monitoring_agent = None
        super(UserServiceMonitoringPublisher, self).__init__(*args, **kwargs)

    def can_update(self, user):
        #Don't allow creation of this model instances for non-admin users also
        return True

    @property
    def target_service(self):
        if getattr(self, "cached_target_service", None):
            return self.cached_target_service
        target_service_id = self.get_attribute("target_service_id")
        if not target_service_id:
            return None
        services = Service.objects.filter(id=target_service_id)
        if not services:
            return None
        target_service = services[0]
        self.cached_target_service = target_service
        return target_service

    @target_service.setter
    def target_service(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("target_service_id", None)):
            self.cached_target_service = None
        self.set_attribute("target_service_id", value)

    @property
    def tenancy_from_target_service(self):
        if getattr(self, "cached_tenancy_from_target_service", None):
            return self.cached_tenancy_from_target_service
        tenancy_from_target_service_id = self.get_attribute("tenancy_from_target_service_id")
        if not tenancy_from_target_service_id:
            return None
        tenancy_from_target_services = ServiceDependency.objects.filter(id=tenancy_from_target_service_id)
        if not tenancy_from_target_services:
            return None
        tenancy_from_target_service = tenancy_from_target_services[0]
        self.cached_tenancy_from_target_service = tenancy_from_target_service
        return tenancy_from_target_service

    @tenancy_from_target_service.setter
    def tenancy_from_target_service(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("tenancy_from_target_service_id", None)):
            self.cached_tenancy_from_target_service = None
        self.set_attribute("tenancy_from_target_service_id", value)

    @property
    def service_monitoring_agent(self):
        if getattr(self, "cached_service_monitoring_agent", None):
            return self.cached_service_monitoring_agent
        service_monitoring_agent_id = self.get_attribute("service_monitoring_agent")
        if not service_monitoring_agent_id:
            return None
        service_monitoring_agents = ServiceDependency.objects.filter(id=service_monitoring_agent_id)
        if not service_monitoring_agents:
            return None
        service_monitoring_agent = service_monitoring_agents[0]
        self.cached_service_monitoring_agent = service_monitoring_agent
        return service_monitoring_agent

    @service_monitoring_agent.setter
    def service_monitoring_agent(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("service_monitoring_agent", None)):
            self.cached_service_monitoring_agent = None
        self.set_attribute("service_monitoring_agent", value)

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a monitoring channel since it creates a slice
                raise XOSProgrammingError("UserServiceMonitoringPublisher's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("UserServiceMonitoringPublisher's self.creator was not set")

        tenancy_from_target_service = None
        if self.pk is None:
            if self.target_service is None:
                raise XOSValidationError("Target service is not specified in UserServiceMonitoringPublisher")
            #Allow only one monitoring publisher for a given service 
            publisher_count = sum ( [1 for publisher in UserServiceMonitoringPublisher.get_tenant_objects().all() if (publisher.target_service.id == self.target_service.id)] )
            if publisher_count > 0:
                raise XOSValidationError("Already %s publishers exist for service. Can only create max 1 UserServiceMonitoringPublisher instances" % str(publisher_count))
            #Create Service composition object here
            tenancy_from_target_service = ServiceDependency(provider_service = self.provider_service,
                                                   subscriber_service = self.target_service)
            tenancy_from_target_service.save()
            self.tenancy_from_target_service = tenancy_from_target_service

            target_uri = CeilometerService.objects.get(id=self.provider_service.id).ceilometer_rabbit_uri
            if target_uri is None:
                raise XOSProgrammingError("Unable to get the Target_URI for Monitoring Agent")
            service_monitoring_agent = ServiceMonitoringAgentInfo(service = self.target_service,
                                                               target_uri = target_uri)
            service_monitoring_agent.save()
            self.service_monitoring_agent = service_monitoring_agent
        
        try:
            super(UserServiceMonitoringPublisher, self).save(*args, **kwargs)
        except:
            if tenancy_from_target_service:
                tenancy_from_target_service.delete()
            if service_monitoring_agent:
                service_monitoring_agent.delete()
            raise

class InfraMonitoringAgentInfo(ServiceMonitoringAgentInfo):
    class Meta:
        app_label = "monitoring"
    start_url = models.TextField(validators=[URLValidator()], help_text="URL/API to be used to start monitoring agent")
    start_url_json_data = models.TextField(help_text="Metadata to be passed along with start API")
    stop_url = models.TextField(validators=[URLValidator()], help_text="URL/API to be used to stop monitoring agent")
    monitoring_publisher = models.ForeignKey(MonitoringPublisher, related_name="monitoring_agents", null=True, blank=True)

class MonitoringCollectorPluginInfo(XOSBase):
    class Meta:
        app_label = "monitoring"
    name = models.CharField(max_length=32)
    plugin_folder_path = StrippedCharField(blank=True, null=True, max_length=1024, help_text="Path pointing to plugin files. e.g. /opt/xos/synchronizers/monitoring/ceilometer/ceilometer-plugins/network/ext_services/vsg/")
    plugin_rabbit_exchange = StrippedCharField(blank=True, null=True, max_length=100) 
    #plugin_notification_handlers_json = models.TextField(blank=True, null=True, help_text="Dictionary of notification handler classes. e.g {\"name\":\"plugin handler main class\"}")
    monitoring_publisher = models.OneToOneField(MonitoringPublisher, related_name="monitoring_collector_plugin", null=True, blank=True)

SFLOW_KIND = "sflow"
SFLOW_PORT = 6343
SFLOW_API_PORT = 33333

class SFlowService(Service):
    KIND = SFLOW_KIND

    class Meta:
        app_label = "monitoring"
        verbose_name = "sFlow Collection Service"
        proxy = True

    default_attributes = {"sflow_port": SFLOW_PORT, "sflow_api_port": SFLOW_API_PORT}

    sync_attributes = ("sflow_port", "sflow_api_port",)

    @property
    def sflow_port(self):
        return self.get_attribute("sflow_port", self.default_attributes["sflow_port"])

    @sflow_port.setter
    def sflow_port(self, value):
        self.set_attribute("sflow_port", value)

    @property
    def sflow_api_port(self):
        return self.get_attribute("sflow_api_port", self.default_attributes["sflow_api_port"])

    @sflow_api_port.setter
    def sflow_api_port(self, value):
        self.set_attribute("sflow_api_port", value)

    def get_instance(self):
        if self.slices.exists():
            slice = self.slices.all()[0]
            if slice.instances.exists():
                return slice.instances.all()[0]

        return None

    @property
    def sflow_api_url(self):
        if not self.get_instance():
            return None
        return "http://" + self.get_instance().get_ssh_ip() + ":" + str(self.sflow_api_port) + "/"

class SFlowTenant(Tenant): 
    class Meta:
        proxy = True

    KIND = SFLOW_KIND

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

    def save(self, *args, **kwargs):
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

        super(SFlowTenant, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(MonitoringChannel, self).delete(*args, **kwargs)

    @property
    def authorized_resource_list(self):
        return ['all']

    @property
    def authorized_resource_list_str(self):
        return ", ".join(self.authorized_resource_list)

