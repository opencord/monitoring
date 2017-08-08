
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


#!/bin/bash
set -x
BASE_KAFKA_VERSION=0.9.0.0
KAFKA_VERSION=2.11-0.9.0.0
export CONF_BASE=$PWD
echo $CONF_BASE
sudo sed -i "s/.*127.0.0.1.*/127.0.0.1 localhost $(hostname)/" /etc/hosts

function install_openjdk_7_jdk {

    echo "Install   openjdk_7_jdk"

    sudo apt-get -y install openjdk-7-jdk

}

function clean_openjdk_7_jdk {

    echo "Clean   openjdk_7_jdk"

    sudo apt-get -y purge openjdk-7-jdk

    sudo apt-get -y autoremove

}

function install_zookeeper {

    echo "Install   Zookeeper"

    sudo apt-get -y install zookeeperd

    sudo cp "${CONF_BASE}"/conf/zookeeper/zoo.cfg /etc/zookeeper/conf/zoo.cfg

    if [[ ${SERVICE_HOST} ]]; then

        sudo sed -i "s/server\.0=127\.0\.0\.1/server.0=${SERVICE_HOST}/g" /etc/zookeeper/conf/zoo.cfg

    fi

    sudo cp "${CONF_BASE}"/conf/zookeeper/myid /etc/zookeeper/conf/myid

    sudo cp "${CONF_BASE}"/conf/zookeeper/environment /etc/zookeeper/conf/environment

    sudo mkdir -p /var/log/zookeeper || true

    sudo chmod 755 /var/log/zookeeper

    sudo cp "${CONF_BASE}"/conf/zookeeper/log4j.properties /etc/zookeeper/conf/log4j.properties

    sudo start zookeeper || sudo restart zookeeper
}

function clean_zookeeper {

    echo "Clean   Zookeeper"

    sudo stop zookeeper || true

    sudo apt-get -y purge zookeeperd

    sudo apt-get -y purge zookeeper

    sudo rm -rf /etc/zookeeper

    sudo rm -rf  /var/log/zookeeper

    sudo rm -rf /var/lib/zookeeper
}

function install_kafka {

    echo "Install   Kafka"

    if [[ "$OFFLINE" != "True" ]]; then
        sudo curl http://apache.mirrors.tds.net/kafka/${BASE_KAFKA_VERSION}/kafka_${KAFKA_VERSION}.tgz \
            -o /root/kafka_${KAFKA_VERSION}.tgz
    fi

    sudo groupadd --system kafka || true

    sudo useradd --system -g kafka kafka || true

    sudo tar -xzf /root/kafka_${KAFKA_VERSION}.tgz -C /opt

    sudo ln -sf /opt/kafka_${KAFKA_VERSION} /opt/kafka

    sudo cp -f "${CONF_BASE}"/conf/kafka/kafka-server-start.sh /opt/kafka_${KAFKA_VERSION}/bin/kafka-server-start.sh

    sudo cp -f "${CONF_BASE}"/conf/kafka/kafka.conf /etc/init/kafka.conf

    sudo chown root:root /etc/init/kafka.conf

    sudo chmod 644 /etc/init/kafka.conf

    sudo mkdir -p /var/kafka || true

    sudo chown kafka:kafka /var/kafka

    sudo chmod 755 /var/kafka

    sudo rm -rf /var/kafka/lost+found

    sudo mkdir -p /var/log/kafka || true

    sudo chown kafka:kafka /var/log/kafka

    sudo chmod 755 /var/log/kafka

    sudo ln -sf /opt/kafka/config /etc/kafka

    sudo cp -f "${CONF_BASE}"/conf/kafka/log4j.properties /etc/kafka/log4j.properties

    sudo chown kafka:kafka /etc/kafka/log4j.properties

    sudo chmod 644 /etc/kafka/log4j.properties

    sudo cp -f "${CONF_BASE}"/conf/kafka/server.properties /etc/kafka/server.properties

    sudo chown kafka:kafka /etc/kafka/server.properties

    sudo chmod 644 /etc/kafka/server.properties

    if [[ ${SERVICE_HOST} ]]; then

        sudo sed -i "s/host\.name=127\.0\.0\.1/host.name=${SERVICE_HOST}/g" /etc/kafka/server.properties
        sudo sed -i "s/zookeeper\.connect=127\.0\.0\.1:2181/zookeeper.connect=${SERVICE_HOST}:2181/g" /etc/kafka/server.properties

    fi

    sudo start kafka || sudo restart kafka
}

function clean_kafka {

    echo "Clean   Kafka"
 
    sudo stop kafka || true

    sudo rm -rf /var/kafka

    sudo rm -rf /var/log/kafka

    sudo rm -rf /etc/kafka

    sudo rm -rf /opt/kafka

    sudo rm -rf /etc/init/kafka.conf

    sudo userdel kafka

    sudo groupdel kafka

    sudo rm -rf /opt/kafka_${KAFKA_VERSION}

    sudo rm -rf /root/kafka_${KAFKA_VERSION}.tgz

}

if [ $1 == "install" ] ; then
   install_openjdk_7_jdk
   install_zookeeper
   install_kafka
   echo "Waiting for kafka and zookeeper to come up"
   sleep 5
   /opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic ceilometer
fi

if [ $1 == "clean" ] ; then
   clean_kafka
   clean_zookeeper
   clean_openjdk_7_jdk
fi

