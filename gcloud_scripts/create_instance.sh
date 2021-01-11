#!/usr/bin/env bash

#nvidia-tesla-k80

INSTANCE_NAME=$1
ZONE=$2
GPU=$3
NUM_GPUS=1

gcloud compute instances create ${INSTANCE_NAME} \
  --zone ${ZONE} \
  --machine-type "n1-standard-4" \
  --subnet "default" \
  --maintenance-policy "TERMINATE" \
  --scopes "https://www.googleapis.com/auth/cloud-platform" \
  --accelerator type=$GPU,count=${NUM_GPUS} \
  --min-cpu-platform "Automatic" \
  --tags "pbtclient" \
  --image-family "ubuntu-1604-lts" \
  --image-project "ubuntu-os-cloud" \
  --boot-disk-size "20" \
  --boot-disk-type "pd-ssd" \
  --boot-disk-device-name "${INSTANCE_NAME}-disk" \
  --metadata-from-file startup-script=./startup.sh
