from xosresource import XOSResource
from services.monitoring.models import MonitoringCollectorPluginInfo

class XOSMonitoringCollectorPluginInfo(XOSResource):
    provides = "tosca.nodes.MonitoringCollectorPluginInfo"
    xos_model = MonitoringCollectorPluginInfo
    copyin_props = ["plugin_folder_path", "plugin_rabbit_exchange"]
