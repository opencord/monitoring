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
from synchronizers.base.syncstep import SyncStep
from synchronizers.base.ansible_helper import run_template_ssh
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from core.models import Service, Slice
from services.monitoring.models import CeilometerService, MonitoringChannel
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
