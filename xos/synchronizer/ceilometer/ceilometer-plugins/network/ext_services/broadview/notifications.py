
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
    cfg.StrOpt('broadview_control_exchange',
               default='broadview_service',
               help="Exchange name for Broadview notifications."),
]

cfg.CONF.register_opts(OPTS)

LOG = log.getLogger(__name__)


class BroadViewNotificationBase(plugin_base.NotificationBase):

    resource_name = None
    event_types = ['broadview.bst.*','broadview.pt.*']

    def get_targets(self,conf):
        """Return a sequence of oslo.messaging.Target

        This sequence is defining the exchange and topics to be connected for
        this plugin.
        """
        LOG.info("SRIKANTH: get_targets for BroadView Notification Listener")
        return [oslo_messaging.Target(topic=topic,
                                      exchange=conf.broadview_control_exchange)
                for topic in self.get_notification_topics(conf)]

    def process_notification(self, message):
        if message['payload']:
            resource_id = 'broadview_' + message["payload"]["asic-id"] 
            volume = 1
            if 'value' in message["payload"]:
                if (not 'ignore-value' in message["payload"]) or (message["payload"]['ignore-value'] != 1):
                    volume = message["payload"]["value"]
            LOG.info('SRIKANTH: Received BroadView %(event_type)s notification: resource_id=%(resource_id)s' % {'event_type': message['event_type'], 'resource_id': resource_id})
            yield sample.Sample.from_notification(
                name=message['event_type'],
                type=sample.TYPE_GAUGE,
                unit='bv-agent',
                volume=volume,
                user_id=None,
                project_id='default_admin_tenant',
                resource_id=resource_id,
                message=message)
