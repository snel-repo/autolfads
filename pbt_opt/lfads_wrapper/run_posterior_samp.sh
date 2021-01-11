
#!/bin/bash

PATH_TO_PS=/snel/home/mreza/projects/PBT_HP_opt/PBT_HP_opt/pbt_opt/lfads_wrapper/run_posterior_mean_sampling.py
max_proc=20

runn=0
for dir in $1/*/
do
	((runn+=1))
    # GPU assignment
    tot_gpu=$((nvidia-smi --query-gpu=gpu_name,gpu_bus_id --format=csv | wc -l) || (echo 0))
    tot_gpu=$((tot_gpu-1))
    # parse job number
    # get gpu device id
    device_no=$((runn % tot_gpu))
	tname=$(basename $dir)
	
	(CUDA_VISIBLE_DEVICES=$device_no python $PATH_TO_PS $dir) &
	#tmux new-session $tname "CUDA_VISIBLE_DEVICES="$device_no" python "$PATH_TO_PS" "$dir" ; tmux wait-for -S "$tname"-done" &
	#wait-for $tname-done &
	if [ "$((runn % max_proc))" -eq 0 ]
	then
		echo "Waiting for the current parallel processes to finish"
		wait
	fi
done