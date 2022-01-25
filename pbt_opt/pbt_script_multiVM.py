import sys
import shutil
import subprocess
import os
from server import Server
from pbt_helper_fn import pbtHelper


### Cloud related parameters
# bucket_name : Bucket name (google cloud storage bucket which acts as the shared storage between the clients and the server)
# data_path : Data directory in the bucket
# run_path : Run directory in the bucket
# name : Run name
bucket_name = 'test-bucket-raghav'
data_path = 'data'
run_path = 'run_x'
name = 'lfadsRunx'

# nprocess_gpu : Number of processes on each client machine/gpu
nprocess_gpu = 3


pbt_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, pbt_path)
helper = pbtHelper(bucket_name, data_path, run_path, name, nprocess_gpu)
my_zone = helper.my_zone
server_id=helper.server_id
machine_name=helper.machine_name
container_name=helper.container_name

subprocess.call(["../gcloud_scripts/mounting.sh {} {} u".format(server_id, bucket_name)], shell=True)
subprocess.call(["../gcloud_scripts/mounting.sh {} {} m".format(server_id, bucket_name)], shell=True)

subprocess.call(["../gcloud_scripts/mounting.sh {} {} u".format(machine_name, bucket_name)], shell=True)
subprocess.call(["../gcloud_scripts/docker_setup.sh {} {} stop".format(machine_name, container_name)], shell=True)

subprocess.call(["../gcloud_scripts/mounting.sh {} {} m".format(machine_name, bucket_name)], shell=True)
subprocess.call(["../gcloud_scripts/docker_setup.sh {} {} start".format(machine_name, container_name)], shell=True)


run_save_path = helper.run_save_path
data_dir = helper.data_dir

# Set PBT machine configuration
computers=helper.computers
nvms = len(helper.vms_list)
nworkers = nprocess_gpu*nvms

# put the pbt run in the pbt_run folder
run_dir = helper.run_dir
run_save_path = os.path.join(run_save_path, run_dir)
server_path = run_save_path

''' create server object '''
server_ip=helper.server_ip

svr = Server(name, run_save_path, num_workers=nworkers, epochs_per_generation=20,
             max_generations=15, explore_method='perturb', explore_param=0.8, 
             mongo_server_ip=server_ip, port=27017, server_log_path=server_path, 
             num_no_best_to_stop=5, docker_name=container_name)


# add machines to be used by PBT
svr.add_computers(computers)

''' Specify the searchable parameters using explorable=True '''

''' ------------------------ Specify model parameters ------------------------ '''
''' Searchable parameters (explorable=True) '''
# Learning rate
svr.add_hp('learning_rate_init', (0.00001, 0.0015), init_sample_mode=[0.001],
           explore_method='perturb', explore_param=0.3, limit_explore=True, explorable=True)

''' Regularization '''
# Standard Dropout
svr.add_hp('keep_prob', (0.4, 1.0), init_sample_mode='rand',
           explore_method='perturb', explore_param=0.3, limit_explore=True, explorable=True)

# Coordinated Dropout
svr.add_hp('keep_ratio', (0.3, 0.9), init_sample_mode=[0.5],
           explore_method='perturb', explore_param=0.3, limit_explore=True, explorable=True)

# L2
svr.add_hp('l2_gen_scale', (1e-5, 1.0), init_sample_mode='logrand', explorable=True)
svr.add_hp('l2_ic_enc_scale', (1e-5, 1.0), init_sample_mode='logrand', explorable=True)

svr.add_hp('l2_con_scale', (1e-5, 1.0), init_sample_mode='logrand', explorable=True)
svr.add_hp('l2_ci_enc_scale', (1e-5, 1.0), init_sample_mode='logrand', explorable=True)

# KL
svr.add_hp('kl_co_weight', (1e-6, 1e-3), init_sample_mode='logrand', explorable=True)
svr.add_hp('kl_ic_weight', (1e-6, 1e-3), init_sample_mode='logrand', explorable=True)



# Change `kl_start_step` and other related params to below:
svr.add_hp('kl_start_epoch', [0])
svr.add_hp('l2_start_epoch', [0])
svr.add_hp('kl_increase_epochs', [80])
svr.add_hp('l2_increase_epochs', [80])

''' Other fixed params (default: explorable=False)'''
# Batch size
svr.add_hp('batch_size', [200])
svr.add_hp('valid_batch_size', [200])

# Validation metric used for PBT
# svr.add_hp('val_cost_for_pbt', ['heldout_samp']) # uncomment for sample validation
svr.add_hp('val_cost_for_pbt', ['heldout_trial'])  # trial (standard validation)

svr.add_hp('cv_keep_ratio', [1.0]) # change (<1) if you use sample validation
svr.add_hp('cd_grad_passthru_prob', [0.0])

# Factors
svr.add_hp('factors_dim', [40])
svr.add_hp('in_factors_dim', [0])

# External inputs
svr.add_hp('ext_input_dim', [0])

# Initial Condition Encoder
svr.add_hp('ic_dim', [64])
svr.add_hp('ic_enc_dim', [64])
svr.add_hp('ic_enc_seg_len', [0])  # for causal encoder, default=0 non-causal

# Generator
svr.add_hp('gen_dim', [64])

# Controller
svr.add_hp('co_dim', [4])
svr.add_hp('ci_enc_dim', [64])
svr.add_hp('con_dim', [64])
svr.add_hp('do_causal_controller', [False])
svr.add_hp('controller_input_lag', [1])

# Output distribution:
svr.add_hp('output_dist', ['poisson'])

# ---- frequently not changed ----
# change if you want to use PBT framework for random search
svr.add_hp('learning_rate_decay_factor', [1])
svr.add_hp('learning_rate_stop', [1e-10])
svr.add_hp('learning_rate_n_to_compare', [0])
svr.add_hp('checkpoint_pb_load_name', ["checkpoint"])

# optimizer params (only search if needed)
svr.add_hp('loss_scale', [1e4])
svr.add_hp('adam_epsilon', [1e-8])
svr.add_hp('beta1', [0.9])
svr.add_hp('beta2', [0.999])

# Data path params
svr.add_hp('data_filename_stem', ['lfads']) # data file must start with this

# Frequently not changed
svr.add_hp('data_dir', [data_dir])
svr.add_hp('do_train_readin', [False])
svr.add_hp('do_train_encoder_only', [False])
svr.add_hp('cv_rand_seed', [1000])
svr.add_hp('output_filename_stem', [""])
svr.add_hp('max_ckpt_to_keep', [1])
svr.add_hp('max_ckpt_to_keep_lve', [1])
svr.add_hp('csv_log', ["fitlog"])
svr.add_hp('checkpoint_name', ["lfads_vae"])
svr.add_hp('device', ["gpu"])
svr.add_hp('ps_nexamples_to_process', [100000000])
svr.add_hp('ic_prior_var', [0.1])
svr.add_hp('ic_post_var_min', [0.0001])
svr.add_hp('co_prior_var', [0.1])
svr.add_hp('co_post_var_min', [0.0001])
svr.add_hp('temporal_spike_jitter_width', [0])
svr.add_hp('inject_ext_input_to_gen', [False])
svr.add_hp('allow_gpu_growth', [True])
svr.add_hp('max_grad_norm', [200.0])
svr.add_hp('do_reset_learning_rate', [True])
svr.add_hp('do_calc_r2', [False])
svr.add_hp('cell_clip_value', [5.0])
svr.add_hp('prior_ar_atau', [10.0])
svr.add_hp('prior_ar_nvar', [0.1])
svr.add_hp('ckpt_save_interval', [1000])
svr.add_hp('do_train_prior_ar_atau', [True])
svr.add_hp('do_train_prior_ar_nvar', [True])
''' --------------------------------------------------------------------- '''

''' Start PBT '''
best_worker, popl = svr.start_pbt()
print(best_worker.run_save_path)

# Posterior Sampling
print("Starting Posterior Sampling ")
best_worker.hps['kind'] = 'posterior_sample_and_average'
best_worker_path = best_worker.run_save_path
best_worker_dir = best_worker_path.split('/')[-1]
best_worker_path_client = '/bucket/{}/{}/{}'.format(run_path, run_dir, best_worker_dir)
jobs=(best_worker.hps, best_worker_path_client)
job_success = best_worker.assign_job(jobs)
w_list =  popl.workers.workers
popl.run_generation_ps()
svr.kill_processes()

# Copy the client logs to shared storage, and create the lfads_output directory (handles all file copy operations)
subprocess.call(["../gcloud_scripts/copy_logs.sh {} {} {}".format(run_path, name, best_worker_dir)], shell=True)
