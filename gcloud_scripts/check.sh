#!/bin/sh
# This script checks if the docker image has been pulled on the client machine

tag_name=$1

for instance in $(gcloud compute instances list --filter="tags:$tag_name AND STATUS:RUNNING" --format="csv[no-heading](name)")
do
	zone=$(gcloud compute instances list --filter="name:$instance" --format="csv[no-heading](zone)")
	varx=$(gcloud compute ssh $instance --command="sudo docker --version" --zone="$zone")
	if echo "$varx" | grep -q "Docker version"; then
		echo "Docker Installed on $instance";
	else
		echo "Docker not installed on $instance";
	fi
done