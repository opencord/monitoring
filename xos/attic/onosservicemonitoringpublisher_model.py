
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


def __init__(self, *args, **kwargs):
    super(ONOSServiceMonitoringPublisher, self).__init__(*args, **kwargs)

def can_update(self, user):
    #Don't allow creation of this model instances for non-admin users also
    return False

def save(self, *args, **kwargs):
    if not self.creator:
        if not getattr(self, "caller", None):
            # caller must be set when creating a monitoring channel since it creates a slice
            raise XOSProgrammingError("ONOSServiceMonitoringPublisher's self.caller was not set")
        self.creator = self.caller
        if not self.creator:
            raise XOSProgrammingError("ONOSServiceMonitoringPublisher's self.creator was not set")

    if self.pk is None:
        #Allow only one openstack monitoring publisher per admin user
        publisher_count = sum ( [1 for onospublisher in ONOSServiceMonitoringPublisher.get_tenant_objects().all() if (onospublisher.creator == self.creator)] )
        if publisher_count > 0:
            raise XOSValidationError("Already %s openstack publishers exist for user Can only create max 1 ONOSServiceMonitoringPublisher instance per user" % str(publisher_count))

    super(ONOSServiceMonitoringPublisher, self).save(*args, **kwargs)