#! /bin/bash

SERVER_NAME="server-2"
NUM_TPU=3
TF_VERSION='nightly'
BUCKET_DIR='gs://pbt-test-bucket-2'
ZONE='us-central1-f'

gcloud config set compute/zone ${ZONE}

#Create a VM with packages required for lfadslite-PBT  (e.g. numpy, h5py, pymongo, etc.)

gcloud compute instances create tmp-${SERVER_NAME}   --machine-type=n1-standard-2 --image-project=ml-images   --image-family=tf-${TF_VERSION}   --scopes=cloud-platform   --zone=${ZONE}   --metadata startup-script="#! /bin/bash
apt-get install -y moreutils
pip install --upgrade pip
hash -r
pip install --upgrade google-cloud-storage
pip install --upgrade pymongo
pip install future
mkdir /data; mkdir -p /code/lfadslite; mkdir -p /code/PBT_HP_opt;

gsutil -m cp -r ${BUCKET_DIR}/data /data
gsutil -m cp -r ${BUCKET_DIR}/code/lfadslite /code/
gsutil -m cp -r  ${BUCKET_DIR}/code/PBT_HP_opt /code/

echo MONGOSERVER=${SERVER_NAME} >> /etc/environment

echo PYTHONPATH=/code/lfadslite:/code/PBT_HP_opt/pbt_opt:$PYTHONPATH >> /etc/environment

"


until gcloud compute ssh tpu-vm --command="cat /etc/environment" | grep -q "lfadslite"; do

  sleep 5

done

#Create an image of the VM instance from previous step

gcloud compute images create tmp-img-${SERVER_NAME} --source-disk tmp-${SERVER_NAME} --source-disk-zone ${ZONE} --family tf-${TF_VERSION} --force

#Create instance template

gcloud compute instance-templates create tmp-template-${SERVER_NAME} --image tmp-img-${SERVER_NAME} --machine-type=n1-standard-2 --scopes=cloud-platform --preemptible --metadata startup-script='#! /bin/bash
#echo TPU_NAME=$(curl -H Metadata-Flavor:Google http://metadata/computeMetadata/v1/instance/hostname | cut -d. -f1) >> /etc/environment
echo PYTHONPATH=/code/lfadslite:/code/PBT_HP_opt/pbt_opt >> /etc/environment'

#Create an instance group

gcloud compute instance-groups managed create group-${SERVER_NAME} --base-instance-name ${SERVER_NAME}  --size ${NUM_TPU} --template tmp-template-${SERVER_NAME} --zone ${ZONE}


#delete tpu-vm
#gcloud compute instances delete tpu-vm -q

