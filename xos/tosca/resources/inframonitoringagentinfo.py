from xosresource import XOSResource
from services.monitoring.models import InfraMonitoringAgentInfo

class XOSInfraMonitoringAgentInfo(XOSResource):
    provides = "tosca.nodes.InfraMonitoringAgentInfo"
    xos_model = InfraMonitoringAgentInfo
    copyin_props = ["start_url", "start_url_json_data", "stop_url"]
