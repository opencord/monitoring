
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


default_attributes = {}
def __init__(self, *args, **kwargs):
    ceilometer_services = CeilometerService.get_service_objects().all()
    if ceilometer_services:
        self._meta.get_field("provider_service").default = ceilometer_services[0].id
    super(MonitoringPublisher, self).__init__(*args, **kwargs)

def can_update(self, user):
    #Allow creation of this model instances for non-admin users also
    return True

@property
def creator(self):
    from core.models import User
    if getattr(self, "cached_creator", None):
        return self.cached_creator
    creator_id=self.get_attribute("creator_id")
    if not creator_id:
        return None
    users=User.objects.filter(id=creator_id)
    if not users:
        return None
    user=users[0]
    self.cached_creator = users[0]
    return user

@creator.setter
def creator(self, value):
    if value:
        value = value.id
    if (value != self.get_attribute("creator_id", None)):
        self.cached_creator=None
    self.set_attribute("creator_id", value)