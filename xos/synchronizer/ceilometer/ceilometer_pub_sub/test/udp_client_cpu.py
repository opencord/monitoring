
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


import socket
import msgpack
from oslo_utils import units
import logging
UDP_IP = "10.11.10.1"
UDP_PORT = 5006

logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s %(message)s',filename='udp_client.log',level=logging.INFO)
udp = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp.bind((UDP_IP, UDP_PORT))
while True:
     data, source = udp.recvfrom(64 * units.Ki)
     #print data
     #try:
     sample = msgpack.loads(data, encoding='utf-8')
     logging.info("%s",sample)
     print sample
     #except Exception:
         #logging.info("%s",sample)
     #    print ("UDP: Cannot decode data sent by %s"), source
