
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
#import threading
import subprocess
import random
import tempfile
#from sshtunnel import SSHTunnelForwarder
from django.db.models import F, Q
from xos.config import Config
from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.ansible_helper import run_template_ssh
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
#from services.monitoring.models import CeilometerService, MonitoringChannel
#from core.models import Service, Slice
from modelaccessor import *
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncCeilometerService(SyncInstanceUsingAnsible):
    provides=[CeilometerService]
    observes=CeilometerService
    requested_interval=0
    template_name = "sync_ceilometerservice.yaml"
    service_key_name = "/opt/xos/synchronizers/monitoring/monitoring_channel_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncCeilometerService, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = CeilometerService.get_service_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
        else:
            objs = CeilometerService.get_deleted_service_objects()

        return objs

    def get_instance(self, o):
        return o.get_instance()

    def get_extra_attributes(self, o):
        fields={}
        fields["instance_hostname"] = o.get_instance().instance_name.replace("_","-")
        #fields = {"instance_hostname": o.get_instance().instance_name.replace("_","-"),
        #          "instance_ip": o.get_instance().private_ip()}


        return fields

    def sync_fields(self, o, fields):
        # the super causes the playbook to be run
        super(SyncCeilometerService, self).sync_fields(o, fields)

    def run_playbook(self, o, fields):
        instance = self.get_instance(o)
        #if (instance.isolation=="container"):
            # If the instance is already a container, then we don't need to
            # install ONOS.
        #    return
        super(SyncCeilometerService,self).run_playbook(o, fields)

    def delete_record(self, m):
        pass
