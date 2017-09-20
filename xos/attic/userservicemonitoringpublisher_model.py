
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

def __xos_save_base(self, *args, **kwargs):
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

    return True     # Indicate that we called super.save()
