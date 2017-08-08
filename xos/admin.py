
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


from django.contrib import admin

from services.monitoring.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import XOSBaseAdmin,ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline, TenantRootTenantInline, TenantRootPrivilegeInline, TenantAttrAsTabInline, UploadTextareaWidget
from core.middleware import get_request

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

class CeilometerServiceForm(forms.ModelForm):
    ceilometer_pub_sub_url = forms.CharField(required=False, max_length=1024, help_text="REST URL of ceilometer PUB/SUB component in http://IP:port/ format")
    ceilometer_enable_pub_sub = forms.BooleanField()

    def __init__(self,*args,**kwargs):
        super (CeilometerServiceForm,self ).__init__(*args,**kwargs)
        if self.instance:
            # fields for the attributes
            self.fields['ceilometer_pub_sub_url'].initial = self.instance.ceilometer_pub_sub_url
            self.fields['ceilometer_enable_pub_sub'].initial = self.instance.ceilometer_enable_pub_sub

    def save(self, commit=True):
        self.instance.ceilometer_pub_sub_url = self.cleaned_data.get("ceilometer_pub_sub_url")
        self.instance.ceilometer_enable_pub_sub = self.cleaned_data.get("ceilometer_enable_pub_sub")
        return super(CeilometerServiceForm, self).save(commit=commit)

    class Meta:
        model = CeilometerService
        fields = '__all__'

class CeilometerServiceAdmin(ReadOnlyAwareAdmin):
    model = CeilometerService
    verbose_name = "Ceilometer Service"
    verbose_name_plural = "Ceilometer Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description','ceilometer_pub_sub_url', 'ceilometer_enable_pub_sub', "view_url","icon_url" ], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'ceilometer_pub_sub_url',)
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]
    form = CeilometerServiceForm

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'Ceilometer Service Details'),
        ('administration', 'Administration'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('ceilometeradmin.html', 'top', 'administration'),
                           )
    #actions=['delete_selected_objects']

    #def get_actions(self, request):
    #    actions = super(CeilometerServiceAdmin, self).get_actions(request)
    #    if 'delete_selected' in actions:
    #        del actions['delete_selected']
    #    return actions

    #def delete_selected_objects(self, request, queryset):
    #    for obj in queryset:
    #        obj.delete()
    #delete_selected_objects.short_description = "Delete Selected Ceilometer Service Objects"

    def get_queryset(self, request):
        return CeilometerService.get_service_objects_by_user(request.user)

class MonitoringChannelForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self,*args,**kwargs):
        super (MonitoringChannelForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = CeilometerService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['creator'].initial = self.instance.creator
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = CEILOMETER_KIND
            self.fields['creator'].initial = get_request().user
            if CeilometerService.get_service_objects().exists():
               self.fields["provider_service"].initial = CeilometerService.get_service_objects().all()[0]


    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        return super(MonitoringChannelForm, self).save(commit=commit)

    class Meta:
        model = MonitoringChannel
        fields = '__all__'

class MonitoringChannelAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'service_specific_attribute',
                                     'ceilometer_url', 'ceilometer_ssh_proxy_url', 'kafka_url', 'tenant_list_str',
                                     'instance', 'creator'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'instance', 'service_specific_attribute', 'ceilometer_url', 'ceilometer_ssh_proxy_url', 'kafka_url', 'tenant_list_str')
    form = MonitoringChannelForm

    suit_form_tabs = (('general','Details'),)
    #actions=['delete_selected_objects']

    #def get_actions(self, request):
    #    actions = super(MonitoringChannelAdmin, self).get_actions(request)
    #    if 'delete_selected' in actions:
    #        del actions['delete_selected']
    #    return actions

    #def delete_selected_objects(self, request, queryset):
    #    for obj in queryset:
    #        obj.delete()
    #delete_selected_objects.short_description = "Delete Selected MonitoringChannel Objects"

    def get_queryset(self, request):
        return MonitoringChannel.get_tenant_objects_by_user(request.user)

class SFlowServiceForm(forms.ModelForm):
    sflow_port = forms.IntegerField(required=False)
    sflow_api_port = forms.IntegerField(required=False)

    def __init__(self,*args,**kwargs):
        super (SFlowServiceForm,self ).__init__(*args,**kwargs)
        if self.instance:
            # fields for the attributes
            self.fields['sflow_port'].initial = self.instance.sflow_port
            self.fields['sflow_api_port'].initial = self.instance.sflow_api_port
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['sflow_port'].initial = SFLOW_PORT
            self.fields['sflow_api_port'].initial = SFLOW_API_PORT

    def save(self, commit=True):
        self.instance.sflow_port = self.cleaned_data.get("sflow_port")
        self.instance.sflow_api_port = self.cleaned_data.get("sflow_api_port")
        return super(SFlowServiceForm, self).save(commit=commit)

    class Meta:
        model = SFlowService
        fields = '__all__'

class SFlowServiceAdmin(ReadOnlyAwareAdmin):
    model = SFlowService
    verbose_name = "SFlow Service"
    verbose_name_plural = "SFlow Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description',"view_url","sflow_port","sflow_api_port","icon_url" ], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]
    form = SFlowServiceForm

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'SFlow Service Details'),
        ('administration', 'Administration'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('sflowadmin.html', 'top', 'administration'),
                           )

    def get_queryset(self, request):
        return SFlowService.get_service_objects_by_user(request.user)

class SFlowTenantForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    listening_endpoint = forms.CharField(max_length=1024, help_text="sFlow listening endpoint in udp://IP:port format")

    def __init__(self,*args,**kwargs):
        super (SFlowTenantForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = SFlowService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['creator'].initial = self.instance.creator
            self.fields['listening_endpoint'].initial = self.instance.listening_endpoint
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = SFLOW_KIND
            self.fields['creator'].initial = get_request().user
            if SFlowService.get_service_objects().exists():
               self.fields["provider_service"].initial = SFlowService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        self.instance.listening_endpoint = self.cleaned_data.get("listening_endpoint")
        return super(SFlowTenantForm, self).save(commit=commit)

    class Meta:
        model = SFlowTenant
        fields = '__all__'

class SFlowTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'creator', 'listening_endpoint' )
    list_display_links = ('backend_status_icon', 'listening_endpoint')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'subscriber_service', 'service_specific_attribute', 'listening_endpoint',
                                     'creator'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'instance', 'service_specific_attribute')
    inlines = [TenantAttrAsTabInline]
    form = SFlowTenantForm

    suit_form_tabs = (('general','Details'), ('tenantattrs', 'Attributes'))

    def get_queryset(self, request):
        return SFlowTenant.get_tenant_objects_by_user(request.user)

class OpenStackServiceMonitoringPublisherForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self,*args,**kwargs):
        super (OpenStackServiceMonitoringPublisherForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = CeilometerService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['creator'].initial = self.instance.creator
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = CEILOMETER_PUBLISH_TENANT_OS_KIND
            self.fields['creator'].initial = get_request().user
            if CeilometerService.get_service_objects().exists():
               self.fields["provider_service"].initial = CeilometerService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        return super(OpenStackServiceMonitoringPublisherForm, self).save(commit=commit)

    class Meta:
        model = OpenStackServiceMonitoringPublisher
        fields = '__all__'

class OpenStackServiceMonitoringPublisherAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'service_specific_attribute', 'creator'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'service_specific_attribute' )
    form = OpenStackServiceMonitoringPublisherForm

    suit_form_tabs = (('general','Details'),)
    actions=['delete_selected_objects']

    def get_actions(self, request):
        actions = super(OpenStackServiceMonitoringPublisherAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_selected_objects(self, request, queryset):
        for obj in queryset:
            obj.delete()
    delete_selected_objects.short_description = "Delete Selected OpenStackServiceMonitoringPublisher Objects"

    def get_queryset(self, request):
        return OpenStackServiceMonitoringPublisher.get_tenant_objects_by_user(request.user)

class ONOSServiceMonitoringPublisherForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    onos_service_endpoints = forms.CharField(max_length=1024, help_text="IP addresses of all the ONOS services to be monitored")

    def __init__(self,*args,**kwargs):
        super (ONOSServiceMonitoringPublisherForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = CeilometerService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['creator'].initial = self.instance.creator
            self.fields['onos_service_endpoints'].initial = self.instance.onos_service_endpoints
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = CEILOMETER_PUBLISH_TENANT_ONOS_KIND
            self.fields['creator'].initial = get_request().user
            if CeilometerService.get_service_objects().exists():
               self.fields["provider_service"].initial = CeilometerService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        self.instance.onos_service_endpoints = self.cleaned_data.get("onos_service_endpoints")
        return super(ONOSServiceMonitoringPublisherForm, self).save(commit=commit)

    class Meta:
        model = ONOSServiceMonitoringPublisher
        fields = '__all__'

class ONOSServiceMonitoringPublisherAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'service_specific_attribute', 'creator', 'onos_service_endpoints'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'service_specific_attribute' )
    form = ONOSServiceMonitoringPublisherForm

    suit_form_tabs = (('general','Details'),)
    actions=['delete_selected_objects']

    def get_actions(self, request):
        actions = super(ONOSServiceMonitoringPublisherAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_selected_objects(self, request, queryset):
        for obj in queryset:
            obj.delete()
    delete_selected_objects.short_description = "Delete Selected OpenStackServiceMonitoringPublisher Objects"

    def get_queryset(self, request):
        return ONOSServiceMonitoringPublisher.get_tenant_objects_by_user(request.user)

class UserServiceMonitoringPublisherForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    exclude_service_list = ['ceilometer', 'onos', 'VTN', 'vROUTER', 'vOLT', 'vTR']
    target_service = forms.ModelChoiceField(queryset=Service.objects.all().exclude(kind__in=exclude_service_list))

    def __init__(self,*args,**kwargs):
        super (UserServiceMonitoringPublisherForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = CeilometerService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['creator'].initial = self.instance.creator
            self.fields['target_service'].initial = self.instance.target_service
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = CEILOMETER_PUBLISH_TENANT_USER_KIND
            self.fields['creator'].initial = get_request().user
            if CeilometerService.get_service_objects().exists():
               self.fields["provider_service"].initial = CeilometerService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        self.instance.target_service = self.cleaned_data.get("target_service")
        return super(UserServiceMonitoringPublisherForm, self).save(commit=commit)

    class Meta:
        model = UserServiceMonitoringPublisher
        fields = '__all__'

class UserServiceMonitoringPublisherAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'service_specific_attribute', 'creator', 'target_service'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'service_specific_attribute' )
    form = UserServiceMonitoringPublisherForm

    suit_form_tabs = (('general','Details'),)
    actions=['delete_selected_objects']

    def get_actions(self, request):
        actions = super(UserServiceMonitoringPublisherAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_selected_objects(self, request, queryset):
        for obj in queryset:
            obj.delete()
    delete_selected_objects.short_description = "Delete Selected UserServiceMonitoringPublisher Objects"

    def get_queryset(self, request):
        return UserServiceMonitoringPublisher.get_tenant_objects_by_user(request.user)

class InfraMonitoringAgentInfoForm(forms.ModelForm):
    class Meta:
        model = InfraMonitoringAgentInfo
        widgets = {
            'start_url_json_data': UploadTextareaWidget(attrs={'rows': 5, 'cols': 80, 'class': "input-xxlarge"}),
        }
        fields = '__all__'

class InfraMonitoringAgentInfoAdmin(XOSBaseAdmin):
    list_display = ('backend_status_icon', 'name', 'id', )
    list_display_links = ('backend_status_icon', 'name', 'id')
    fieldsets = [ (None, {'fields': ['name', 'start_url', 'start_url_json_data', 'stop_url', 'monitoring_publisher'],
                          'classes':['suit-tab suit-tab-general']})]
    form = InfraMonitoringAgentInfoForm

    suit_form_tabs = (('general','Details'),)

class MonitoringCollectorPluginInfoForm(forms.ModelForm):
    class Meta:
        model = MonitoringCollectorPluginInfo
        #widgets = {
        #    'plugin_notification_handlers_json': UploadTextareaWidget(attrs={'rows': 5, 'cols': 80, 'class': "input-xxlarge"}),
        #}
        fields = '__all__'

class MonitoringCollectorPluginInfoAdmin(XOSBaseAdmin):
    list_display = ('backend_status_icon', 'name', 'id', )
    list_display_links = ('backend_status_icon', 'name', 'id')
    fieldsets = [ (None, {'fields': ['name', 'plugin_folder_path', 'plugin_rabbit_exchange', 'monitoring_publisher'],
                          'classes':['suit-tab suit-tab-general']})]
    form = MonitoringCollectorPluginInfoForm

    suit_form_tabs = (('general','Details'),)

admin.site.register(CeilometerService, CeilometerServiceAdmin)
admin.site.register(SFlowService, SFlowServiceAdmin)
admin.site.register(MonitoringChannel, MonitoringChannelAdmin)
admin.site.register(SFlowTenant, SFlowTenantAdmin)
admin.site.register(OpenStackServiceMonitoringPublisher, OpenStackServiceMonitoringPublisherAdmin)
admin.site.register(ONOSServiceMonitoringPublisher, ONOSServiceMonitoringPublisherAdmin)
admin.site.register(UserServiceMonitoringPublisher, UserServiceMonitoringPublisherAdmin)
admin.site.register(InfraMonitoringAgentInfo, InfraMonitoringAgentInfoAdmin)
admin.site.register(MonitoringCollectorPluginInfo, MonitoringCollectorPluginInfoAdmin)

