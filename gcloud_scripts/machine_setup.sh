#!/bin/bash

base_name=$1
num_machine=$2
zone=$3
gpu=${4:-"nvidia-tesla-k80"}

gpu_node_counter=0

while [ $gpu_node_counter -lt $num_machine ]
	do
	gpu_node_counter=$((gpu_node_counter+1))
	machine_name="$base_name$gpu_node_counter"
	echo "creating $machine_name"
	sh create_instance.sh $machine_name $zone $gpu
	done