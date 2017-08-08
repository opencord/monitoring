
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


#!/usr/bin/python
from flask import request, Request, jsonify
from flask import Flask
from flask import make_response
import logging
import logging.handlers
import logging.config
import subprocess
import ConfigParser
import generate_pipeline
app = Flask(__name__)


@app.route('/monitoring/agent/openstack/start',methods=['POST'])
def openstack_start():
    try:
        # To do validation of user inputs for all the functions
        target = request.json['target']
        logging.debug("target:%s",target)
        if not generate_pipeline.onos_service_info:
            logging.debug (" ONOS Service is not enalble,Only openstack need to be enabled ")
            generate_pipeline.generate_pipeline_yaml_for_openstack(target,True)
        else:
            logging.debug(" ONOS Service is also enabled ,please generate yaml file for both onos and openstack")
            generate_pipeline.generate_pipeline_yaml_for_openstack_onos(target,True)
        restart_ceilometer_services() 
        return "Openstack start service called \n"
    except Exception as e:
            return e.__str__()

@app.route('/monitoring/agent/onos/start',methods=['POST'])
def onos_start():
    try:
        target = request.json['target']
        logging.debug("target:%s",target)
        resources = request.json['resources'] 
        logging.debug("resources:%s",resources)
        if not generate_pipeline.openstack_service_info:
            logging.debug("Openstak Service is not enabled,Only ONOS need to be enabled")
            generate_pipeline.generate_pipeline_yaml_for_onos(target,resources,True)
        else:
            logging.debug(" Openstack Service is also enabled ,please generate yaml file for both onos and openstack")
            generate_pipeline.generate_pipeline_yaml_for_onos_openstack(target,resources,True)

        restart_ceilometer_services() 
        return "ONOS start service called \n"
    except Exception as e:
            return e.__str__()

@app.route('/monitoring/agent/vsg/start',methods=['POST'])
def vsg_start():
    try:
        target = request.json['target']
        logging.debug("target:%s",target)
        return "vsg start service called \n"
    except Exception as e:
            return e.__str__()


@app.route('/monitoring/agent/openstack/stop',methods=['POST'])
def openstack_stop():
    try:
        target = request.json['target']
        logging.debug("target:%s",target)
        if not generate_pipeline.onos_service_info:
             generate_pipeline.generate_pipeline_yaml_for_openstack(target,False)
        else:
             generate_pipeline.generate_pipeline_yaml_for_onos(generate_pipeline.onos_service_info[0].target,generate_pipeline.onos_service_info[0].resources,True)
        logging.debug("Delete Openstack object")
        for obj in generate_pipeline.openstack_service_info:
               generate_pipeline.openstack_service_info.remove(obj)
   
        restart_ceilometer_services() 
        return "Openstack stop service called \n"
      
    except Exception as e:
            return e.__str__()

@app.route('/monitoring/agent/onos/stop',methods=['POST'])
def onos_stop():
    try:
        target = request.json['target']
        logging.debug("target:%s",target)
        metadata = request.json['meta_data'] 
        logging.debug("metadata:%s",metadata)
        resources = metadata['resources']
        logging.debug("resources:%s",resources)
         
        if not generate_pipeline.openstack_service_info:
             generate_pipeline.generate_pipeline_yaml_for_onos(target,resources,False)
        else:
            generate_pipeline.generate_pipeline_yaml_for_openstack(generate_pipeline.openstack_service_info[0].target,True)

        logging.debug("Delete ONOS Object")
        for obj in generate_pipeline.onos_service_info:
               generate_pipeline.onos_service_info.remove(obj)

        restart_ceilometer_services() 
        return "ONOS stop service called \n"
    except Exception as e:
            return e.__str__()

@app.route('/monitoring/agent/vsg/stop',methods=['POST'])
def vsg_stop():
    try:
        target = request.json['target']
        logging.debug("target:%s",target)
        return "vsg stop service called \n"
    except Exception as e:
            return e.__str__()


def restart_ceilometer_services():
    try :
       config = ConfigParser.ConfigParser()
       config.read('monitoring_agent.conf')
       services = config.get('SERVICE','Ceilometer_service')
       service = services.split(",")
       subprocess.call("sudo cp pipeline.yaml /etc/ceilometer/pipeline.yaml",shell=True)
    except Exception as e:
        logging.error("* Error in confing file:%s",e.__str__())
        return False
    else :
        for service_name in service:
            command = ['service',service_name, 'restart'];
            logging.debug("Executing: %s command",command)
            #shell=FALSE for sudo to work.
            try :
                subprocess.call(command, shell=False)
            except Exception as e:
                logging.error("* %s command execution failed with error %s",command,e.__str__())
                return False
    return True

if __name__ == "__main__":
    logging.config.fileConfig('monitoring_agent.conf', disable_existing_loggers=False)
    app.run(host="0.0.0.0",port=5004,debug=False)
