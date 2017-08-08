
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
from services.monitoring.models import OpenStackServiceMonitoringPublisher, CeilometerService, InfraMonitoringAgentInfo, MonitoringCollectorPluginInfo

class XOSOpenStackMonitoringPublisher(XOSResource):
    provides = "tosca.nodes.OpenStackMonitoringPublisher"
    xos_model = OpenStackServiceMonitoringPublisher
    name_field = None

    def get_xos_args(self, throw_exception=True):
        args = super(XOSOpenStackMonitoringPublisher, self).get_xos_args()

        # PublisherTenant must always have a provider_service
        provider_name = self.get_requirement("tosca.relationships.TenantOfService", throw_exception=True)
        if provider_name:
            args["provider_service"] = self.get_xos_object(Service, throw_exception=True, name=provider_name)

        return args

    def postprocess(self, obj):
        for ma_name in self.get_requirements("tosca.relationships.ProvidesInfraMonitoringAgentInfo"):
            ma = self.get_xos_object(InfraMonitoringAgentInfo, name=ma_name)
            ma.monitoring_publisher = obj
            ma.save()
        for mcp_name in self.get_requirements("tosca.relationships.ProvidesMonitoringCollectorPluginInfo"):
            mcp = self.get_xos_object(MonitoringCollectorPluginInfo, name=mcp_name)
            mcp.monitoring_publisher = obj
            mcp.save()

    def get_existing_objs(self):
        args = self.get_xos_args(throw_exception=False)
        return OpenStackServiceMonitoringPublisher.get_tenant_objects().filter(provider_service=args["provider_service"])

    def can_delete(self, obj):
        return super(XOSOpenStackMonitoringPublisher, self).can_delete(obj)

