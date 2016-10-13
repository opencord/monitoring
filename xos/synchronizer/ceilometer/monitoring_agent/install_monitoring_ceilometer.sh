#! /bin/bash
#set -x 
COMPUTENODES=$( bash -c "source ~/service-profile/cord-pod/admin-openrc.sh ; nova hypervisor-list" |grep "cord.lab"|awk '{print $4}')

echo $COMPUTENODES

for NODE in $COMPUTENODES; do
    ansible-playbook -i /etc/maas/ansible/pod-inventory ~/xos_services/monitoring/xos/synchronizer/ceilometer/monitoring_agent/ceilometer_config.yaml -e instance_name=$NODE
done

CEILOMETERNODE="ceilometer-1"
ansible-playbook ~/xos_services/monitoring/xos/synchronizer/ceilometer/monitoring_agent/ceilometer_config.yaml -e instance_name=$CEILOMETERNODE
