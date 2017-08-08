
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


from xosresource import XOSResource
from core.models import Tenant, Service
from services.monitoring.models import UserServiceMonitoringPublisher, CeilometerService, InfraMonitoringAgentInfo, MonitoringCollectorPluginInfo

class XOSUserServiceMonitoringPublisher(XOSResource):
    provides = "tosca.nodes.UserServiceMonitoringPublisher"
    xos_model = UserServiceMonitoringPublisher
    name_field = None

    def get_xos_args(self, throw_exception=True):
        args = super(XOSUserServiceMonitoringPublisher, self).get_xos_args()

        # PublisherTenant must always have a provider_service
        provider_name = self.get_requirement("tosca.relationships.TenantOfService", throw_exception=True)
        if provider_name:
            args["provider_service"] = self.get_xos_object(Service, throw_exception=True, name=provider_name)

        target_service_name = self.get_requirement("tosca.relationships.PublishesMonitoringData", throw_exception=True)
        if target_service_name:
            args["target_service"] = self.get_xos_object(Service, throw_exception=True, name=target_service_name)

        return args

    def get_existing_objs(self):
        args = self.get_xos_args(throw_exception=False)
        return [publisher for publisher in UserServiceMonitoringPublisher.get_tenant_objects().all() if (publisher.target_service.id == args["target_service"].id)]

    def postprocess(self, obj):
        #for ma_name in self.get_requirements("tosca.relationships.ProvidesMonitoringAgentInfo"):
        #    ma = self.get_xos_object(MonitoringAgentInfo, name=ma_name)
        #    ma.monitoring_publisher = obj
        #    ma.save()
        for mcp_name in self.get_requirements("tosca.relationships.ProvidesMonitoringCollectorPluginInfo"):
            mcp = self.get_xos_object(MonitoringCollectorPluginInfo, name=mcp_name)
            mcp.monitoring_publisher = obj
            mcp.save()

    def can_delete(self, obj):
        return super(XOSUserServiceMonitoringPublisher, self).can_delete(obj)

