#!/bin/bash

docker_tag="220124"
base_name="pbtclient"
u='snelbeta'
p='$Cr}ZqK:mg68)Vny'
docker_login="docker login --username='$u' --password='$p'"
docker_pull="docker pull snelbeta/radical:${docker_tag}"

for instance in $(gcloud compute instances list --filter="tags:$base_name AND STATUS:RUNNING" --format="csv[no-heading](name)")

do
	zone=$(gcloud compute instances list --filter="name:$instance" --format="csv[no-heading](zone)")
	gcloud compute ssh $instance --command="$docker_login" --zone=$zone
	gcloud compute ssh $instance --command="$docker_pull" --zone=$zone
done
