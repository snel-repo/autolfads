#!/bin/bash

# $1 is the tmux name
# $2 is the "hostid_processnumber"
# $3 is project (and database) name

MY_PATH="`dirname \"$0\"`"              # relative
MY_PATH="`( cd \"$MY_PATH\" && pwd )`"  # absolutized and normalized

# get number of GPU devices
#    # if using GPU
#    tot_gpu=$((nvidia-smi --query-gpu=gpu_name,gpu_bus_id --format=csv | wc -l) || (echo 0))
#    tot_gpu=$((tot_gpu-1))
#    # parse job number
#    runn=$(echo $2 | grep -o -E '[0-9]+')
#    # get gpu device id
#    device_no=$((runn % tot_gpu))
#else
#    # if using CPU
 device_no=0

#runn=$(echo $2 | grep -o -E '[0-9]+')
if [ -z "$MONGOSERVER" ]
then
    tmux -L pbt_server kill-session -t $2 2> /dev/null
    tmux -L pbt_server new-session -d -s $2 "CUDA_VISIBLE_DEVICES="$device_no" python "$MY_PATH"/lfads_client.py "$3" "$4" "$1" "$5" |& tee >(ts \"%y-%m-%d %H_%M_%S\" |& tee -a /tmp/pbt_"$4"_"$3".log)"
    tmux -L pbt_server set -t $1 remain-on-exit on 2> /dev/null
else
    device_name="tpu-"$MONGOSERVER"-"$1

    tmux -L pbt_server kill-session -t $2 2> /dev/null
    tmux -L pbt_server new-session -d -s $2 "TPU_NAME="$device_name" python "$MY_PATH"/lfads_client.py "$3" "$4" "$1" |& tee >(ts \"%y-%m-%d %H_%M_%S\" |& tee -a /tmp/pbt_"$4"_"$3".log)"
#tmux -L pbt_server new-session -d -s $2 "TPU_NAME="$device_name" python "$MY_PATH"/lfads_client.py "$3" "$4" "$1""
    tmux -L pbt_server set -t $2 remain-on-exit on 2> /dev/null
#sleep 0.1
fi
