
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


default_attributes = {"sflow_port": SFLOW_PORT, "sflow_api_port": SFLOW_API_PORT}

sync_attributes = ("sflow_port", "sflow_api_port",)

@property
def sflow_port(self):
    return self.get_attribute("sflow_port", self.default_attributes["sflow_port"])

@sflow_port.setter
def sflow_port(self, value):
    self.set_attribute("sflow_port", value)

@property
def sflow_api_port(self):
    return self.get_attribute("sflow_api_port", self.default_attributes["sflow_api_port"])

@sflow_api_port.setter
def sflow_api_port(self, value):
    self.set_attribute("sflow_api_port", value)

def get_instance(self):
    if self.slices.exists():
        slice = self.slices.all()[0]
        if slice.instances.exists():
            return slice.instances.all()[0]

    return None

@property
def sflow_api_url(self):
    if not self.get_instance():
        return None
    return "http://" + self.get_instance().get_ssh_ip() + ":" + str(self.sflow_api_port) + "/"
