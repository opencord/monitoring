#!/bin/sh
sudo apt-get update
sudo apt-get install -y python-dev
sudo pip install Flask
cd /home/ubuntu/monitoring_agent
chmod +x monitoring_agent.py
nohup python monitoring_agent.py &
