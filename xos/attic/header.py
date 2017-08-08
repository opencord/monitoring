
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


# Monitoring models
from django.db import models
from django.core.validators import URLValidator
from core.models import Service, PlCoreBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, ServiceDependency, ServiceMonitoringAgentInfo
from core.models.plcorebase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
import traceback
from xos.exceptions import *
from core.models import SlicePrivilege, SitePrivilege
from sets import Set
from urlparse import urlparse

class ConfigurationError(Exception):
    pass


CEILOMETER_KIND = "ceilometer"
#Ensure the length of name for 'kind' attribute is below 30
CEILOMETER_PUBLISH_TENANT_KIND = "ceilo-publish-tenant"
CEILOMETER_PUBLISH_TENANT_OS_KIND = "ceilo-os-publish-tenant"
CEILOMETER_PUBLISH_TENANT_ONOS_KIND = "ceilo-onos-publish-tenant"
CEILOMETER_PUBLISH_TENANT_USER_KIND = "ceilo-user-publish-tenant"
