
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


#!/bin/sh

declare -a plugins=("vcpe= ceilometer.network.ext_services.vcpe.notifications:VCPENotification"
"vcpe.compute.stats= ceilometer.network.ext_services.vcpe.notifications:VCPEComputeStatistics"
"vcpe.dns.cache.size=ceilometer.network.ext_services.vcpe.notifications:VCPEDNSCacheSize"
"vcpe.dns.total_instered_entries=ceilometer.network.ext_services.vcpe.notifications:VCPEDNSTotalInsertedEntries"
"vcpe.dns.replaced_unexpired_entries= ceilometer.network.ext_services.vcpe.notifications:VCPEDNSReplacedUnexpiredEntries"
"vcpe.dns.queries_answered_locally= ceilometer.network.ext_services.vcpe.notifications:VCPEDNSQueriesAnsweredLocally"
"vcpe.dns.queries_forwarded= ceilometer.network.ext_services.vcpe.notifications:VCPEDNSQueriesForwarded"
"vcpe.dns.server.queries_sent= ceilometer.network.ext_services.vcpe.notifications:VCPEDNSServerQueriesSent"
"vcpe.dns.server.queries_failed= ceilometer.network.ext_services.vcpe.notifications:VCPEDNSServerQueriesFailed"
"volt.device= ceilometer.network.ext_services.volt.notifications:VOLTDeviceNotification"
"volt.device.subscribers= ceilometer.network.ext_services.volt.notifications:VOLTDeviceSubscriberNotification"
"infra=ceilometer.network.ext_services.openstack_infra.notifications:OPENSTACK_INFRANotification"
"cord=ceilometer.network.ext_services.cord.notifications:CORDNotificationBase"
"broadview.bst.device=ceilometer.network.ext_services.broadview.notifications:BroadViewNotificationBase")

section='ceilometer.notification'
for line in "${plugins[@]}"
do
   sed -i -e '/\['$section'\]/{;:a;n;/^$/!ba;i\'"$line"'' -e '}' /usr/local/lib/python2.7/dist-packages/ceilometer*egg*/entry_points.txt
done

