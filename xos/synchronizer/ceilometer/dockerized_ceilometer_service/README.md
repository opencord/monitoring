# dockerized-monitoring service

NOTE: This is a WIP activity and not completed yet

The target of this activity is to containarize all the components that constitute CORD Monitoring service

Following are the various modules in CORD Monitoring service

Infrastructure components:
- Rabbitmq
- Kafka & Zookeeper
- MongoDB
- KeyStone
- MySQL DB for KeyStone
CORD specific/extended components:
- Ceilometer-notification-agent
- Ceilometer-api
- CORD Publish/Subscribe module on top of Ceilometer data

The plan is to leverage publicly available containers for all the infrastructure components as much as possible.
However, in our exploration, we found that public offcial docker images are not available for many of the above components.
Instead, there are private docker images available, but there is a risk associated in terms of maintenance and support for such images
For CORD specific components, we need to create the docker container ourselves.

Below are the steps to create custom VM images with all the above necessary containers to be used by XOS (TODO: Create Ansible script for the same and refer to it)
1. Create ubuntu 14.04 based VM
2. Install Docker: wget -qO- https://get.docker.com/ | sh
3. Add user to docker group: sudo usermod -aG docker $USER
4. Install docker-compose
5. docker pull rabbitmq:3-management
6. docker pull spotify/kafka
7. docker pull mongo:3.4
8. docker pull srikanthvavila/ceilometer-agent-notification
9. docker pull srikanthvavila/cord-publish-subscribe
10. copy dockerized_ceilometer_service/docker-compose.yml file (Pending: The IP addresses need to be parameterized so that they can be provided when the VM is actually booted)


While instantiating monitoring service in CORD:
1. Ensure the IP addresses are updated with the VM's fabric interface IP address
2. docker-compose up -d


PENDING:
1. Build ceilometer-api container the same way ceilometer-agent-notification is built
2. Explore availability of docker container for MySQL DB 
3. Explore availability of Keystone docker container (Explore https://github.com/int32bit/docker-keystone)
4. Configuration of MySQL DB and Keystone to allow ceilometer-api to provide its services
5. Currently spotify/kafka container embeds the zookeeper service also. Explore availability of container image for kafka and zookeeper such that kafka can be scaled independently (Explore https://github.com/wurstmeister/kafka-docker)
6. Explore if MongoDB can be replaced with Gnocchi component and update ceilometer-agent-notification/Dockerfile to do corresponding Gnocchi related configurations. Once migration to Gnocchi is completed, ceilometer-api conatiner is not needed, instead Gnocchi API will be used 
