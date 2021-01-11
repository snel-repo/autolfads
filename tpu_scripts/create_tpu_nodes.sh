#! /bin/bash

ind=0
for INSTANCE in $(gcloud compute instance-groups managed list-instances tpu-vm-group --zone=us-central1-f --format='value(NAME)')

do

  gcloud alpha compute tpus create ${INSTANCE} --range 10.240.${ind}.0/29 --zone us-central1-f --version 1.9 --network default

  ind=$((ind+2))
done
