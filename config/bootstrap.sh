#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install python-pip git --yes
sudo pip install virtualenv
virtualenv ip
. ip/bin/activate
pip install -r /vagrant/requirements/local.txt
cp /vagrant/config/bash_profile.sh /home/vagrant/.bash_profile
