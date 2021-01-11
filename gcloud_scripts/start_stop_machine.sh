#!/bin/sh

command=$1
machine=$2

instance_list=$(gcloud compute instances list --filter="tags:$machine AND STATUS:RUNNING" --format="csv[no-heading](name)")
for instance in $instance_list
	do
		zone=$(gcloud compute instances list --filter="name:$instance" --format="csv[no-heading](zone)")
		echo "$command $instance"
		gcloud compute instances $command $instance --zone=$zone
	done
