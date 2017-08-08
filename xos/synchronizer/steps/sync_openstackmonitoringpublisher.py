
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


import hashlib
import os
import socket
import sys
import base64
import time
import json
#import threading
import subprocess
import random
import tempfile
#from sshtunnel import SSHTunnelForwarder
from django.db.models import F, Q
from xos.config import Config
from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.ansible_helper import run_template
from synchronizers.new_base.ansible_helper import run_template_ssh
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from modelaccessor import *
#from core.models import Service, Slice
#from services.monitoring.models import CeilometerService, OpenStackServiceMonitoringPublisher
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncOpenStackMonitoringPublisher(SyncInstanceUsingAnsible):
    provides=[OpenStackServiceMonitoringPublisher]
    observes=OpenStackServiceMonitoringPublisher
    requested_interval=0
    template_name = "sync_openstackmonitoringpublisher.yaml"

    def __init__(self, *args, **kwargs):
        super(SyncOpenStackMonitoringPublisher, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = OpenStackServiceMonitoringPublisher.get_tenant_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
        else:
            objs = OpenStackServiceMonitoringPublisher.get_deleted_tenant_objects()

        return objs

    def sync_record(self, o):
        logger.info("sync'ing object %s" % str(o),extra=o.tologdict())

        self.prepare_record(o)

        ceilometer_services = CeilometerService.get_service_objects().filter(id=o.provider_service.id)
        if not ceilometer_services:
            raise "No associated Ceilometer service"
        ceilometer_service = ceilometer_services[0]
        service_instance = ceilometer_service.get_instance()
        # sync only when the corresponding service instance is fully synced
        if not service_instance:
            self.defer_sync(o, "waiting on associated service instance")
            return
        if not service_instance.instance_name:
            self.defer_sync(o, "waiting on associated service instance.instance_name")
            return

        # Step1: Orchestrate UDP proxy agent on the compute node where monitoring service VM is spawned

        fields = { "hostname": ceilometer_service.ceilometer_rabbit_compute_node,
                   "baremetal_ssh": True,
                   "instance_name": "rootcontext",
                   "username": "root",
                   "container_name": None,
                   "rabbit_host": ceilometer_service.ceilometer_rabbit_host,
                   "rabbit_user": ceilometer_service.ceilometer_rabbit_user,
                   "rabbit_password": ceilometer_service.ceilometer_rabbit_password,
		   "listen_ip_addr": socket.gethostbyname(ceilometer_service.ceilometer_rabbit_compute_node)
	}

        # If 'o' defines a 'sync_attributes' list, then we'll copy those
        # attributes into the Ansible recipe's field list automatically.
        if hasattr(o, "sync_attributes"):
            for attribute_name in o.sync_attributes:
                fields[attribute_name] = getattr(o, attribute_name)

        key_name = self.get_node_key(service_instance.node)
        if not os.path.exists(key_name):
            raise Exception("Node key %s does not exist" % key_name)
        key = file(key_name).read()
        fields["private_key"] = key

        template_name = "sync_openstackmonitoringpublisher.yaml"
        fields["ansible_tag"] =  o.__class__.__name__ + "_" + str(o.id) + "_step1"

        self.run_playbook(o, fields, template_name)

        # Step2: Orchestrate OpenStack publish agent
        target_uri = "udp://" + ceilometer_service.ceilometer_rabbit_compute_node + ":4455"
        fields = {}
        agent_info = []
        if o.monitoring_agents:
           for agent in o.monitoring_agents.all():
              body = {'target': target_uri}
              if agent.start_url_json_data:
                 start_url_dict = json.loads(agent.start_url_json_data)
                 body.update(start_url_dict)
              a = {'url': agent.start_url, 'body': json.dumps(body)}
              agent_info.append(a)

        fields["agents"] = agent_info 
        #fields["private_key"] = ""

        template_name = "enable_monitoring_service.yaml"
        fields["ansible_tag"] =  o.__class__.__name__ + "_" + str(o.id) + "_step2"

        run_template(template_name, fields, object=o)

    def map_delete_inputs(self, o):
        fields = {"unique_id": o.id,
                  "delete": True}
        return fields

    def delete_record(self, o):
        pass

