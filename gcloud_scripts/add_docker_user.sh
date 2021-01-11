#!/bin/bash

# This is script is used to add user to the docker groups on the client machines

base_name=$1
add_user="sudo usermod -a -G docker $USER"

for instance in $(gcloud compute instances list --filter="tags:$base_name AND STATUS:RUNNING" --format="csv[no-heading](name)")
do
	zone=$(gcloud compute instances list --filter="name:$instance" --format="csv[no-heading](zone)")
	echo $instance
	gcloud compute ssh $instance --command="$add_user" --zone=$zone
	echo "added $add_user to the docker group on $instance"
done
