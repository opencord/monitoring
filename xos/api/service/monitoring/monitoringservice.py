
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


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.views import APIView
from core.models import *
from django.forms import widgets
from django.conf.urls import patterns, url
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField
from django.shortcuts import get_object_or_404
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from xos.exceptions import *
import json
import subprocess
from django.views.decorators.csrf import ensure_csrf_cookie
from services.monitoring.models import MonitoringChannel, CeilometerService

class CeilometerServiceForApi(CeilometerService):
    class Meta:
        proxy = True
        app_label = "ceilometer"

    @property
    def related(self):
        related = {}
        if self.creator:
            related["creator"] = self.creator.username
        instance = self.get_instance()
        if instance:
            related["instance_id"] = instance.id
            related["instance_name"] = instance.name
            if instance.node:
                related["compute_node_name"] = instance.node.name
        return related


class CeilometerServiceSerializer(PlusModelSerializer):
        id = ReadOnlyField()
        backend_status = ReadOnlyField()
        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
        ceilometer_pub_sub_url = ReadOnlyField()
        ceilometer_enable_pub_sub = ReadOnlyField()
        kafka_url = ReadOnlyField()
        related = serializers.DictField(required=False)

        class Meta:
            model = CeilometerServiceForApi
            fields = ('humanReadableName',
                      'id',
                      'backend_status',
                      'ceilometer_pub_sub_url',
                      'ceilometer_enable_pub_sub',
                      'kafka_url',
                      'related')

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

# @ensure_csrf_cookie
class CeilometerServiceViewSet(XOSViewSet):
    base_name = "monitoringservice"
    method_name = None # use the api endpoint /api/service/monitoring/
    method_kind = "viewset"
    queryset = CeilometerServiceForApi.get_service_objects().select_related().all()
    serializer_class = CeilometerServiceSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(CeilometerServiceViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns

    def list(self, request):
        object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(object_list, many=True)

        return Response(serializer.data)

