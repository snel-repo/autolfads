#!/bin/bash

# Copies the client logs from the tmp folder to the mounted shared storage, and copies the final 
# best worker to the lfads_output directory in the run folder

run_path=$1
name=$2
best_worker=$3
logs_dir="client_logs"
base_name="pbtclient"

new_dir="/bucket/$run_path/$logs_dir/"
cmd="mkdir -p $new_dir ; cd /tmp ; cp pbt_$name* $new_dir"
cmd_docker="docker exec docker_pbt bash -c \"$cmd\""

for instance in $(gcloud compute instances list --filter="tags:$base_name AND STATUS:RUNNING" --format="csv[no-heading](name)")

do
	zone=$(gcloud compute instances list --filter="name:$instance" --format="csv[no-heading](zone)")
	gcloud compute ssh $instance --command="$cmd_docker" --zone=$zone
	sleep 2
done

run_dir="$HOME/bucket/$run_path/"
output_dir="lfads_output"
output_path="${run_dir}${output_dir}/"
zip_path="$HOME/bucket/${run_path}.zip"
mkdir -p $output_path
best_worker_path="${run_dir}pbt_run/${best_worker}/."
cp -a $best_worker_path $output_path
zip -r $zip_path $run_dir -i '*.log' '*.csv' '*.txt' '*.json' '*.h5*' &> /dev/null

echo "${run_path}.zip created."
echo "You can download the zip file from the storage bucket."
