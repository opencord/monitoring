
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
