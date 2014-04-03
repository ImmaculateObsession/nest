#!/usr/bin/env bash

echo "==================== START ===================="
cd /home/vagrant/
rm -rf /home/vagrant/.bash_profile
ln -s /vagrant/config/bash_profile.sh /home/vagrant/.bash_profile
echo "==================== INSTALL DEPENDENCIES ===================="
sudo apt-get update
sudo apt-get install python-pip git curl make sqlite3 postgresql postgresql-server-dev-9.1 libpq-dev python-dev --yes
sudo gem update --system
sudo gem install compass
sudo pip install virtualenv
echo "==================== SETUP DB ===================="
sudo su postgres -c "createuser -s vagrant"
psql -c "ALTER USER vagrant PASSWORD 'vagrant';"
createdb nest
echo "==================== SETUP VIRTUALENV ===================="
virtualenv ip
curl https://raw.github.com/creationix/nvm/master/install.sh | sh
. /home/vagrant/.bash_profile
. ip/bin/activate
pip install -r /vagrant/requirements/local.txt
pip install -r /vagrant/requirements.txt
echo "==================== SETUP NODE ===================="
nvm install 0.10
nvm use 0.10
npm install grunt-cli -g
cd /home/vagrant/nest/static/
npm install
grunt
echo "==================== DONE ===================="

