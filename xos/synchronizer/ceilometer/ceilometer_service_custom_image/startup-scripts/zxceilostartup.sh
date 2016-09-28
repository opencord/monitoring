#!/bin/sh
PUB_SUB_PATH=/home/ubuntu/monitoring/xos/synchronizer/ceilometer/ceilometer_pub_sub
echo $PWD
cd $PUB_SUB_PATH
sleep 5
chmod +x sub_main.py
nohup ./sub_main.py &
echo $PWD
cd -
echo $PWD
