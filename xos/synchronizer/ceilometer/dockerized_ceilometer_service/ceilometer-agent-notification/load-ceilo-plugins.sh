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

