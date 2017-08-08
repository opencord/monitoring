
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
from modelaccessor import *
#from core.models import Service, Slice, ModelLink
#from services.monitoring.models import CeilometerService, MonitoringChannel
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

#FIXME: Is this right approach?
#Maintaining a global SSH tunnel database in order to handle tunnel deletions during the object delete
ssh_tunnel_db = {}

class SSHTunnel:

    def __init__(self, localip, localport, key, remoteip, remote_port, jumpuser, jumphost):
        self.key = key
        self.remote_host = remoteip        # Remote ip on remotehost
        self.remote_port = remote_port
        # Get a temporary file name
        tmpfile = tempfile.NamedTemporaryFile()
        tmpfile.close()
        self.socket = tmpfile.name
        self.local_port = localport
        self.local_host = localip
        self.jump_user = jumpuser        # Remote user on remotehost
        self.jump_host = jumphost        # What host do we send traffic to
        self.open = False

    def start(self):
        logger.info("Creating SSH Tunnel: ssh -MfN -S %s -i %s -L %s:%s:%s;%s -o ExitOnForwardFailure=True %s@%s"%(self.socket, self.key, self.local_host, self.local_port, self.remote_host, self.remote_port,self.jump_user,self.jump_host))
        exit_status = subprocess.call(['ssh', '-MfN',
            '-S', self.socket,
            '-i', self.key,
            '-L', '{}:{}:{}:{}'.format(self.local_host, self.local_port, self.remote_host, self.remote_port),
            '-o', 'ExitOnForwardFailure=True',
            self.jump_user + '@' + self.jump_host
        ])
        if exit_status != 0:
            raise Exception('SSH tunnel failed with status: {}'.format(exit_status))
        if self.send_control_command('check') != 0:
            raise Exception('SSH tunnel failed to check')
        self.open = True

    def stop(self):
        if self.open:
            if self.send_control_command('exit') != 0:
                raise Exception('SSH tunnel failed to exit')
            self.open = False

    def send_control_command(self, cmd):
        return subprocess.check_call(['ssh', '-S', self.socket, '-O', cmd, '-l', self.jump_user, self.jump_host])

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()


#class SshTunnel(threading.Thread):
#    def __init__(self, localip, localport, remoteip, remoteport, proxy_ssh_key, jumpuser, jumphost):
#        threading.Thread.__init__(self)
#        self.localip = localip          # Local ip to listen to
#        self.localport = localport      # Local port to listen to
#        self.remoteip = remoteip        # Remote ip on remotehost
#        self.remoteport = remoteport    # Remote port on remotehost
#        self.proxy_ssh_key = proxy_ssh_key
#        self.jumpuser = jumpuser        # Remote user on remotehost
#        self.jumphost = jumphost        # What host do we send traffic to
#        self.daemon = True              # So that thread will exit when
#                                        # main non-daemon thread finishes
#
#    def run(self):
#        if subprocess.call([
#            'ssh', '-N',
#                   '-i', self.proxy_ssh_key,
#                   '-L', self.localip + ':' + str(self.localport) + ':' + self.remoteip + ':' + str(self.remoteport),
#                   jumpuser + '@' + jumphost ]):
#            raise Exception ('ssh tunnel setup failed')

class SyncMonitoringChannel(SyncInstanceUsingAnsible):
    provides=[MonitoringChannel]
    observes=MonitoringChannel
    requested_interval=0
    template_name = "sync_monitoringchannel.yaml"
    service_key_name = "/opt/xos/synchronizers/monitoring/monitoring_channel_private_key"
    watches = [ModelLink(Slice,via='slice')]

    def __init__(self, *args, **kwargs):
        super(SyncMonitoringChannel, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = MonitoringChannel.get_tenant_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
        else:
            objs = MonitoringChannel.get_deleted_tenant_objects()

        return objs

    def get_extra_attributes(self, o):
        # This is a place to include extra attributes. In the case of Monitoring Channel, we need to know
        #   1) Allowed tenant ids
        #   2) Ceilometer API service endpoint URL if running externally
        #   3) Credentials to access Ceilometer API service

        ceilometer_services = CeilometerService.get_service_objects().filter(id=o.provider_service.id)
        if not ceilometer_services:
            raise "No associated Ceilometer service"
        ceilometer_service = ceilometer_services[0]
        ceilometer_pub_sub_url = ceilometer_service.ceilometer_pub_sub_url
        if not ceilometer_pub_sub_url:
            ceilometer_pub_sub_url = ''
        instance = self.get_instance(o)

        try:
            full_setup = Config().observer_full_setup
        except:
            full_setup = True

        fields = {"unique_id": o.id,
                  "allowed_tenant_ids": o.tenant_list,
                  "auth_url":ceilometer_service.ceilometer_auth_url,
                  "admin_user":ceilometer_service.ceilometer_admin_user,
                  "admin_password":ceilometer_service.ceilometer_admin_password,
                  "admin_tenant":ceilometer_service.ceilometer_admin_tenant,
                  "ceilometer_pub_sub_url": ceilometer_pub_sub_url,
                  "full_setup": full_setup}

        return fields

    def sync_fields(self, o, fields):
        try:
           super(SyncMonitoringChannel, self).sync_fields(o, fields)

           #Check if ssh tunnel is needed
           proxy_ssh = getattr(Config(), "observer_proxy_ssh", False)

           if proxy_ssh and (not o.ssh_proxy_tunnel):
               proxy_ssh_key = getattr(Config(), "observer_proxy_ssh_key", None)
               proxy_ssh_user = getattr(Config(), "observer_proxy_ssh_user", "root")
               jump_hostname = fields["hostname"]

               #Get the tunnel detsination               
               remote_host = o.nat_ip
               remote_port = o.ceilometer_port
               #FIXME: For now, trying to setup the tunnel on the local port same as the remote port
               local_port = remote_port
               local_ip = socket.gethostbyname(socket.gethostname())

               tunnel = SSHTunnel(local_ip, local_port, proxy_ssh_key, remote_host, remote_port, proxy_ssh_user, jump_hostname)
               tunnel.start()
               logger.info("SSH Tunnel created for Monitoring channel-%s at local port:%s"%(o.id,local_port))

               #FIXME:Store the tunnel handle in global tunnel database
               ssh_tunnel_db[o.id] = tunnel

               #Update the model with ssh tunnel info
               o.ssh_proxy_tunnel = True
               o.ssh_tunnel_ip = local_ip
               o.ssh_tunnel_port = local_port

        except Exception,error:
           raise Exception(error)

    def run_playbook(self, o, fields):
        #ansible_hash = hashlib.md5(repr(sorted(fields.items()))).hexdigest()
        #quick_update = (o.last_ansible_hash == ansible_hash)

        #if quick_update:
        #    logger.info("quick_update triggered; skipping ansible recipe")
        #else:
        if ('delete' in fields) and (fields['delete']):
            logger.info("Delete for Monitoring channel-%s is getting synchronized"%(o.id))
            if o.id in ssh_tunnel_db:
                tunnel = ssh_tunnel_db[o.id]
                tunnel.stop()
                logger.info("Deleted SSH Tunnel for Monitoring channel-%s at local port:%s"%(o.id,o.ssh_tunnel_port))
                o.ssh_proxy_tunnel = False
                del ssh_tunnel_db[o.id]
        super(SyncMonitoringChannel, self).run_playbook(o, fields)

        #o.last_ansible_hash = ansible_hash

    def map_delete_inputs(self, o):
        fields = {"unique_id": o.id,
                  "delete": True}
        return fields

    def handle_watched_object(self, o):
        logger.info("handle_watched_object is invoked for object %s" % (str(o)),extra=o.tologdict())
        if (type(o) is Slice):
           self.handle_slice_watch_notification(o)
        pass

    def handle_slice_watch_notification(self, sliceobj):
        logger.info("handle_slice_watch_notification: A slice %s is created or updated or deleted" % (sliceobj))
        for obj in MonitoringChannel.get_tenant_objects().all():
            #Save the monitoring channel object to reflect the newly updated slice
            obj.save()
        pass
