STARTUP_PATH="/home/ubuntu/monitoring/xos/synchronizer/ceilometer/ceilometer_service_custom_image/startup-scripts"
IP=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep "10.0.3")
#IP=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep "10.11.10")
echo $IP
sudo rabbitmqctl add_user openstack "password"
sudo rabbitmqctl set_permissions openstack ".*" ".*" ".*"
python $STARTUP_PATH/update-endpoints.py --username root --password password --host localhost --endpoint $IP --endpoint-type public
python $STARTUP_PATH/update-endpoints.py --username root --password password --host localhost --endpoint $IP --endpoint-type admin
