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
