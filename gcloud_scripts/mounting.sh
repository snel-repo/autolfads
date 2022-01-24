#!/bin/sh

# Script to mount the shared storage bucket on the clients. Inputs are tag name, zone, bucket name operation - in that order

base_name=$1
cloud_bucket=$2
operation="$3"

home_bucket='$HOME/bucket'

cmd_mkdir="mkdir -p $home_bucket"
cmd_mount="/usr/bin/gcsfuse -o allow_other $cloud_bucket $home_bucket"
cmd_unmount="fusermount -u $home_bucket"
instance_list=$(gcloud compute instances list --filter="tags:$base_name AND STATUS:RUNNING" --format="csv[no-heading](name)")

if [ "${operation}" = "m" ]; then
	for instance in $instance_list
	do
		zone=$(gcloud compute instances list --filter="name:$instance" --format="csv[no-heading](zone)")
		echo "mounting $instance"
		gcloud compute ssh $instance --command="$cmd_mkdir" --zone=$zone
		gcloud compute ssh $instance --command="$cmd_mount" --zone=$zone
	done
fi


if [ "${operation}" = "u" ]; then
	for instance in $instance_list
	do
		zone=$(gcloud compute instances list --filter="name:$instance" --format="csv[no-heading](zone)")
		echo "unmounting $instance"
		gcloud compute ssh $instance --command="$cmd_unmount" --zone=$zone
	done
fi

if [ "${operation}" != "m" -a "${operation}" != "u" ]; then
	echo "Error - Use ' m ' for mounting, ' u ' for unmounting. Do not recognize the ' $operation ' argument"
fi
