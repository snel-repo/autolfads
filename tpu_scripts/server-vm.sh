#! /bin/bash

TF_VERSION='nightly'
BUCKET_DIR='gs://pbt-test-bucket-2'
ZONE='us-central1-f'
SERVER_NAME="server-3"
NUM_TPU=3

gcloud config set compute/zone ${ZONE}

gcloud compute instances create ${SERVER_NAME} --machine-type=n1-standard-4 --boot-disk-size=30GB --image-project=ml-images --image-family=tf-${TF_VERSION} --zone=${ZONE} --scopes=cloud-platform  --tags=server-tag --metadata startup-script="#! /bin/bash
gcloud config set compute/zone ${ZONE}
apt-get install dirmngr
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
echo 'deb http://repo.mongodb.org/apt/debian stretch/mongodb-org/4.0 main' | tee /etc/apt/sources.list.d/mongodb-org-4.0.list
apt-get update
sudo apt-get install -y mongodb-org
echo 'mongodb-org hold' | sudo dpkg --set-selections
echo 'mongodb-org-server hold' | sudo dpkg --set-selections
echo 'mongodb-org-shell hold' | sudo dpkg --set-selections
echo 'mongodb-org-mongos hold' | sudo dpkg --set-selections
echo 'mongodb-org-tools hold' | sudo dpkg --set-selections
mkdir -p /db/db_data
systemctl enable mongod.service
systemctl start mongod.service

apt-get install -y moreutils
pip install --upgrade pip
hash -r
pip install --upgrade google-cloud-storage
pip install --upgrade pymongo
pip install future

mkdir /data; mkdir -p /code/lfadslite; mkdir -p /code/PBT_HP_opt;

gsutil -m cp -r ${BUCKET_DIR}/data/* /data/
gsutil -m cp -r ${BUCKET_DIR}/code/lfadslite /code/
gsutil -m cp -r  ${BUCKET_DIR}/code/PBT_HP_opt /code/

echo HOSTNAME=${SERVER_NAME} >> /etc/environment
echo MONGOSERVER=${SERVER_NAME} >> /etc/environment

echo PYTHONPATH=/code/lfadslite:/code/PBT_HP_opt/pbt_opt:$PYTHONPATH >> /etc/environment
"

until gcloud compute ssh ${SERVER_NAME} --command="cat /etc/environment" | grep -q "lfadslite"; do
  sleep 5
done

gcloud compute ssh ${SERVER_NAME} --zone=us-central1-f --command='sudo mongo admin --host 127.0.0.1:27017 --eval "db.createUser({user: \"pbt_user\", pwd: \"pbt0Pass\", roles: [ { role: \"userAdminAnyDatabase\", db: \"admin\" }]});db.grantRolesToUser(\"pbt_user\", [{ role: \"readWriteAnyDatabase\", db: \"admin\" }]);" && sudo sed -i "/bindIp/d" /etc/mongod.conf && echo "security:
   authorization: enabled
net: 
   bindIp: 127.0.0.1,`hostname -I`" | sudo tee -a /etc/mongod.conf && sudo systemctl restart mongod.service'


#create TPU nodes
ind=1
tpu_node_counter=0
TPU_RANGE_LIST=$(gcloud beta compute tpus list --zone=${ZONE} --format='value(RANGE)')

while [ $tpu_node_counter -lt $NUM_TPU ]
do
    ip_range=10.240.${ind}.0/29
    if ! echo $TPU_RANGE_LIST | grep -q $ip_range; then
        echo $ip_range
        gcloud compute tpus create tpu-${SERVER_NAME}-${tpu_node_counter} --range ${ip_range} --zone ${ZONE} --version ${TF_VERSION} --preemptible --network default &
        tpu_node_counter=$((tpu_node_counter+1))
    fi
    ind=$((ind+1))
done
