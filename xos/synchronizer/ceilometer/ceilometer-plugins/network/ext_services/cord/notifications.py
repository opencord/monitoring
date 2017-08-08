
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


#
# Copyright 2012 New Dream Network, LLC (DreamHost)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Handler for producing network counter messages from Neutron notification
   events.

"""

import oslo_messaging
from oslo_config import cfg

from ceilometer.agent import plugin_base
from oslo_log import log
from ceilometer import sample

OPTS = [
    cfg.StrOpt('cord_control_exchange',
               default='cord',
               help="Exchange name for CORD related notifications."),
]

cfg.CONF.register_opts(OPTS)

LOG = log.getLogger(__name__)


class CORDNotificationBase(plugin_base.NotificationBase):

    resource_name = None
    event_types = ['cord*']

    def get_targets(self,conf):
        """Return a sequence of oslo.messaging.Target

        This sequence is defining the exchange and topics to be connected for
        this plugin.
        """
        LOG.info("get_targets for CORD Notification Listener")
        return [oslo_messaging.Target(topic=topic,
                                      exchange=conf.cord_control_exchange)
                for topic in self.get_notification_topics(conf)]

    def process_notification(self, message):
        LOG.info('Received CORD notification')
        if 'counter_type' not in message['payload']:
            meter_type = sample.TYPE_GAUGE
        else:
            meter_type = sample.TYPE_GAUGE if 'gauge' in message['payload']['counter_type'].lower() else sample.TYPE_DELTA if 'delta' in message['payload']['counter_type'].lower() else sample.TYPE_GAUGE

        yield sample.Sample.from_notification(
            name=message['payload']['counter_name'],
            type=meter_type,
            unit=message['payload']['counter_unit'],
            volume=message['payload']['counter_volume'],
            user_id=message['payload']['user_id'],
            project_id=message['payload']['tenant_id'],
            resource_id=message['payload']['resource_id'],
            message=message)
