
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


import kafka
import kafka_broker
from oslo_utils import netutils
import logging

def read_notification_from_ceilometer_over_kafka(parse_target):
    logging.info("Kafka target:%s",parse_target)
    try :
        kafka_publisher=kafka_broker.KafkaBrokerPublisher(parse_target)
        for message in kafka_publisher.kafka_consumer:
            #print message.value
            logging.info("%s",message.value)
            #print status
    except Exception as e:
        logging.error("Error in Kafka setup:%s ",e.__str__())

ceilometer_client="kafka://10.11.10.1:9092?topic=test"
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s %(message)s',filename='kafka_client.log',level=logging.INFO)
parse_target=netutils.urlsplit(ceilometer_client)
read_notification_from_ceilometer_over_kafka(parse_target)
