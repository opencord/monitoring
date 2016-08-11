#!/bin/sh
sudo sed -i "s/.*127.0.0.1.*/127.0.0.1 localhost $(hostname)/" /etc/hosts
STARTUP_PATH=/home/ubuntu/monitoring/xos/synchronizer/ceilometer/ceilometer_service_custom_image/startup-scripts
PUB_SUB_PATH=/home/ubuntu/monitoring/xos/synchronizer/ceilometer/ceilometer_pub_sub
$STARTUP_PATH/ceilometer_init_script.sh
echo $PWD
cd $PUB_SUB_PATH
sleep 5
chmod +x sub_main.py
nohup ./sub_main.py &
echo $PWD
cd -
echo $PWD
