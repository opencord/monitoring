
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


# (C) Copyright Broadcom Corporation 2016
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from broadviewpublisherbase import BroadViewPublisherBase
from kombu.connection import BrokerConnection
from kombu.messaging import Exchange, Queue, Consumer, Producer
import six
import uuid
import datetime
from broadview_collector.serializers.bst_to_ceilometer import BSTToCeilometer
from broadview_collector.serializers.pt_to_ceilometer import PTToCeilometer
import json
import ConfigParser
import sys

try:
    from oslo_log import log 
except:
    import logging as log

LOG = log.getLogger(__name__)

class BroadViewPublisher(BroadViewPublisherBase):
    def readConfig(self):
        try:
            bvcfg = ConfigParser.ConfigParser()
            bvcfg.read("/etc/broadviewcollector.conf")
            self.rabbit_user = bvcfg.get("ceilometer", "rabbit_user")
            self.rabbit_password = bvcfg.get("ceilometer", "rabbit_password") 
            self.rabbit_host = bvcfg.get("ceilometer", "rabbit_host") 
            self.rabbit_exchange = bvcfg.get("ceilometer", "rabbit_exchange") 
        except:
            LOG.info("BroadViewPublisher: unable to read configuration")

    def errback(self, exc, interval):
        LOG.error('Error: %r', exc, exc_info=1)
        LOG.info('Retry in %s seconds.', interval)
   
    def setup_rabbit_mq_channel(self):
        ceilometer_exchange = Exchange(self.rabbit_exchange, "topic", durable=False)
        # connections/channels
        connection = BrokerConnection(self.rabbit_host, self.rabbit_user, self.rabbit_password)
        LOG.info("BroadViewPublisher: Connection to RabbitMQ server successful")
        channel = connection.channel()
        # produce
        self._producer = Producer(channel, exchange=ceilometer_exchange, routing_key='notifications.info')
        self._publish = connection.ensure(self._producer, self._producer.publish, errback=self.errback, max_retries=3)

    def __init__(self):
        self.rabbit_user = 'openstack'
        self.rabbit_password = 'password'
        self.rabbit_host = '1.2.3.4'
        self.rabbit_exchange = 'broadview_service'
        self._producer = None
        self._publish = None
        self.readConfig()
        LOG.info("BroadViewPublisher: Ceilometer Publisher Initialized")

    def publish(self, host, data):
        code = 500
        #  get a producer if needed
        if not self._producer:
            self.setup_rabbit_mq_channel()
        if self._producer: 
            code = 200
        if self.isBST(data):
            success, sdata = BSTToCeilometer().serialize(host, data)
        elif self.isPT(data):
            self._topic = "broadview-pt"
            success, sdata = PTToCeilometer().serialize(host, data)
        else:
            success = False
        if success:
            sdata = json.loads(sdata)
            if success: 
                for x in sdata:
                    try:
                        #self._producer.publish(x)
                        self._publish(x)
                        LOG.debug("BroadViewPublisher: Sent data to ceilometer exchange")
                    except Exception as e:
                        LOG.info('exception: {}'.format(e))
                        LOG.info('unable to send to ceilometer exchange {}: {}'.format(self.rabbit_exchange, sys.exc_info()[0]))
            else:
                code = 500
        return code

    def __repr__(self):
        return "BroadView Ceilometer Publisher {} {}".format(self.rabbit_host, self.rabbit_exchange) 

