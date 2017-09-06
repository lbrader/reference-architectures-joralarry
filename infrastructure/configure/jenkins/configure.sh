#!/bin/bash


exec >> >(tee /tmp/provision.log)
exec 2>&1

set -xe

sudo apt install -y python-pip unzip
sudo pip install --upgrade ansible
cd /tmp
rm -rf joara
unzip -q ansible-jenkins.zip
cd joara/joara-main/infrastructure/configure/jenkins/ansible-jenkins/
env | sort
export PATH=/home/$USER/.local/bin:$PATH
ansible-playbook --connection=local -i hosts.ini jenkins.yml