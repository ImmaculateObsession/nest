#!/usr/bin/env bash

cd /home/vagrant/
rm -rf /home/vagrant/.bash_profile
ln -s /vagrant/config/bash_profile.sh /home/vagrant/.bash_profile
sudo apt-get update
sudo apt-get install python-pip git curl --yes
sudo pip install virtualenv
virtualenv ip
curl https://raw.github.com/creationix/nvm/master/install.sh | sh
. /home/vagrant/.bash_profile
. ip/bin/activate
pip install -r /vagrant/requirements/local.txt
nvm install 0.10
nvm use 0.10
npm install grunt-cli -g
cd /home/vagrant/nest/static/
npm install
grunt

