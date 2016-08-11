set -x
echo $PWD
export CMDIR=$PWD
echo $CMDIR

echo "-------------------------------------------------------------------"
echo " --------------------Installing Ceilometer-------------------------"
echo "-------------------------------------------------------------------"
cd $CMDIR/mitaka-v2
sh install_ansible.sh
echo $'[local]\nlocalhost' | sudo tee --append /etc/ansible/hosts > /dev/null
ansible-playbook -c local os_ceilometer_mitaka.yml 
source admin-openrc.sh
echo "-------------------------------------------------------------------"

echo "-------------------------------------------------------------------"
echo " --------------------Installing Kafka------------------------------"
echo "-------------------------------------------------------------------"
sudo apt-get -y install python-pip
sudo pip install kafka
sudo pip install flask
cd $CMDIR/kafka-installer/
./install_zookeeper_kafka.sh install
cd $CMDIR 
echo "-------------------------------------------------------------------"


echo "-------------------------------------------------------------------"
echo " --------------------Installing InitScript-------------------------"
echo "-------------------------------------------------------------------"
cd $CMDIR/startup-scripts
echo " Installing startup script"
sudo cp zxceilostartup.sh /etc/init.d
sudo chmod a+x /etc/init.d/zxceilostartup.sh
sudo update-rc.d zxceilostartup.sh defaults
chmod 755 $CMDIR/startup-scripts/ceilometer_init_script.sh
echo "-------------------------------------------------------------------"
