
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


from jinja2 import Environment, FileSystemLoader
from urlparse import urlparse
import os

# Capture our current directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

openstack_service_info=[]
onos_service_info=[]
class Openstack_Service():
   def __init__(self,service_name,target):
      self.service_name=service_name
      self.target=target
      self.service_enable=True
   def update_openstack_service_info(self):
       if not openstack_service_info:
           openstack_service_info.append(self)
       else:
           for obj in openstack_service_info:
               openstack_service_info.remove(obj)
           openstack_service_info.append(self)
           #openstack_service_info[0].target.append(target)
         
class Onos_Service():
   def __init__(self,service_name,target,resources):
      self.service_name=service_name
      self.target=target
      self.resources=resources
      self.service_enable=True
   def update_onos_service_info(self):
       if not onos_service_info:
          onos_service_info.append(self)
       else:
           for obj in onos_service_info:
               onos_service_info.remove(obj)
           onos_service_info.append(self)
          #onos_service_info[0].target.append(target)

def generate_pipeline_yaml_for_openstack(target,Flag):
    # Create the jinja2 environment.
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    op_service=Openstack_Service("OPENSTACK",target)
    op_service.update_openstack_service_info() 
    parse_target=urlparse(target)
    host = parse_target.hostname
    port =  parse_target.port
    with open("pipeline.yaml", 'w') as f:
        j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)
        context = {
             'openstack' : Flag, 
             'listen_ip_addr': host,
             'port_number' : port
        }
        fp = j2_env.get_template('pipeline.yaml.j2').render (
            context)
        f.write(fp)

def generate_pipeline_yaml_for_onos(target,resources,Flag):
     
    onos_service=Onos_Service("ONOS",target,resources)
    onos_service.update_onos_service_info() 
    with open("pipeline.yaml", 'w') as f:
        j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)
        context = {
             'onos' : Flag,
             'onos_endpoints' : resources,
             'onos_target' : target,
             'new_line': '\n',
             'new_tab': '      '    
        }
        fp = j2_env.get_template('pipeline.yaml.j2').render (
            context)
        f.write(fp)

def generate_pipeline_yaml_for_openstack_onos(target,Flag):

    op_service=Openstack_Service("OPENSTACK",target)
    op_service.update_openstack_service_info() 
    parse_target=urlparse(target)
    host = parse_target.hostname
    port =  parse_target.port
    with open("pipeline.yaml", 'w') as f:
        j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)
        context = {
             'openstack' : Flag, 
             'listen_ip_addr': host,
             'port_number' : port,
             'onos' : Flag,
             'onos_endpoints' : onos_service_info[0].resources,
             'onos_target' : onos_service_info[0].target,
             'new_line': '\n',
             'new_tab': '      '
        }
        fp = j2_env.get_template('pipeline.yaml.j2').render (
            context)
        f.write(fp)

def generate_pipeline_yaml_for_onos_openstack(target,resources,Flag):

    onos_service=Onos_Service("ONOS",target,resources)
    onos_service.update_onos_service_info() 
 
    parse_target=urlparse(openstack_service_info[0].target)
    host = parse_target.hostname
    port =  parse_target.port
   
    with open("pipeline.yaml", 'w') as f:
        j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)
        context = {
             'onos' : Flag,
             'onos_endpoints' : resources,
             'onos_target' : target,
             'new_line': '\n',
             'new_tab': '      ',
             'openstack' : Flag,
             'listen_ip_addr': host,
             'port_number' : port
        }
        fp = j2_env.get_template('pipeline.yaml.j2').render (
            context)
        f.write(fp)
