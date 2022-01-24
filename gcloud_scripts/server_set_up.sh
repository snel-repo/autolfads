#! /bin/bash

SERVER_NAME=$1
ZONE=$2

gcloud config set compute/zone ${ZONE}

gcloud compute instances create ${SERVER_NAME} --machine-type=n1-standard-4 --boot-disk-size=300GB --image-project=deeplearning-platform-release --image=tf-1-15-cpu-20200424 --zone=${ZONE} --scopes=cloud-platform  --tags=${SERVER_NAME} --metadata startup-script="#! /bin/bash
gcloud config set compute/zone ${ZONE}
apt-get install dirmngr
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
echo 'deb http://repo.mongodb.org/apt/debian stretch/mongodb-org/4.0 main' | tee /etc/apt/sources.list.d/mongodb-org-4.0.list
apt-get update
apt-get install -y mongodb-org
echo 'mongodb-org hold' | dpkg --set-selections
echo 'mongodb-org-server hold' | dpkg --set-selections
echo 'mongodb-org-shell hold' | dpkg --set-selections
echo 'mongodb-org-mongos hold' | dpkg --set-selections
echo 'mongodb-org-tools hold' | dpkg --set-selections
mkdir -p /db/db_data
systemctl enable mongod.service
systemctl start mongod.service

apt-get install -y moreutils
pip2 install -- upgrade pip2
hash -r
pip2 install --upgrade google-cloud-storage
pip2 install --upgrade pymongo
pip2 install future
pip2 install grpcio==1.30.0
pip2 install protobuf==3.12.2
pip2 install tensorflow==1.14.0

echo 'deb http://packages.cloud.google.com/apt gcsfuse-stretch main' | sudo tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
yes | sudo apt-get install gcsfuse

sudo sed -i '8 s/^#//' /etc/fuse.conf

echo HOSTNAME=${SERVER_NAME} >> /etc/environment
echo MONGOSERVER=${SERVER_NAME} >> /etc/environment
echo PATH=/code/test-pbt-bucket/code/lfadslite:$PATH >> /etc/environment
echo PYTHONPATH=/code/test-pbt-bucket/code/lfadslite:/code/test-pbt-bucket/code/PBT_HP_opt/pbt_opt:$PYTHONPATH >> /etc/environment
"

sleep 40
varxy=$(gcloud compute ssh ${SERVER_NAME} --command="hostname" --zone=${ZONE} 2>/dev/null)
out=$?
sleep_time=40
if [ $out -eq 255 ]
then
        echo "Server boot-up incomplete. Wait for $sleep_time s"
        sleep $sleep_time
elif [ $out -eq 0 ]
then
        echo "Server boot-up completed"
else
        echo "exit status is $out"
fi

#until gcloud compute ssh ${SERVER_NAME} --zone=${ZONE} --command="cat /etc/environment | grep -q lfadslite" ; do
#  sleep 5
#done

gcloud compute ssh ${SERVER_NAME} --zone=${ZONE} --command='sudo mongo admin --host 127.0.0.1:27017 --eval "db.createUser({user: \"pbt_user\", pwd: \"pbt0Pass\", roles: [ { role: \"userAdminAnyDatabase\", db: \"admin\" }]});db.grantRolesToUser(\"pbt_user\", [{ role: \"readWriteAnyDatabase\", db: \"admin\" }]);" && sudo sed -i "/bindIp/d" /etc/mongod.conf && echo "security:
   authorization: enabled
net: 
   bindIp: 127.0.0.1,`hostname -I`" | sudo tee -a /etc/mongod.conf && sudo systemctl restart mongod.service'
