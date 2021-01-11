#!/bin/bash

SERVER_NAME=''
ZONE=''

function start {

	SERVER_NAME="$1"
	ZONE="$2"
	NUM_TPU="$3"

	gcloud compute instances start ${SERVER_NAME} --zone=${ZONE} -q &

	tpu_node_counter=0
	while [ $tpu_node_counter -lt $NUM_TPU ]
		do
		gcloud compute tpus start tpu-${SERVER_NAME}-${tpu_node_counter} --zone=${ZONE} &
		tpu_node_counter=$((tpu_node_counter+1))
		done

	echo "Starting TPU nodes"

}

function stop {

	SERVER_NAME="$1"
	ZONE="$2"
	NUM_TPU="$3"

	gcloud compute instances stop ${SERVER_NAME} --zone=${ZONE} -q &


	tpu_node_counter=0
	while [ $tpu_node_counter -lt $NUM_TPU ]
		do
		gcloud compute tpus stop tpu-${SERVER_NAME}-${tpu_node_counter} --zone=${ZONE} &
		tpu_node_counter=$((tpu_node_counter+1))
		done

	echo "Stopping TPU nodes"


}

function delete {

	SERVER_NAME="$1"
	ZONE="$2"
	NUM_TPU="$3"

	gcloud compute instances delete ${SERVER_NAME} --zone=${ZONE} -q &

	tpu_node_counter=0
	while [ $tpu_node_counter -lt $NUM_TPU ]
		do
		gcloud compute tpus delete tpu-${SERVER_NAME}-${tpu_node_counter} --zone=${ZONE} -q &
		tpu_node_counter=$((tpu_node_counter+1))
		done

	echo "Deleting TPU nodes"

}



if [ "$1" == 'help' -o "$1" == '-help' -o "$1" == '--help' ]
	then
		echo "Specify one of the following task: create, stop, delete server instance"
		echo "To start a server instance run: bash /server-manager.sh start <server_name> <zone> <num_tpus>"
		echo "To stop a server instance and tpus run: bash /server-manager.sh stop <server_name> <zone> <num_tpus>"
		echo "To delete a server instnace run: bash /server-manager.sh delete <server_name> <zone> <num_tpus>"
	else
		echo "Running task ${1}"
		${@:1}
	fi

