import sys
import subprocess
import os
from server import Server
#from lfads_wrapper.lfads_wrapper import lfadsWrapper
from lfads_wrapper.run_posterior_mean_sampling import run_posterior_sample_and_average, copy_output

server_id = os.environ["HOSTNAME"]
print(server_id)
# get the zone
my_zone = subprocess.check_output([
                'gcloud','compute','instances','list', '--filter', 'name=("%s")' % server_id, '--format', 'csv[no-heading](zone)' ])[:-1]
# get the number of TPUs
tpu_name_list = subprocess.check_output(['gcloud','beta','compute', 'tpus', 'list', '--zone', my_zone, '--format', 'value(NAME)']).split('\n')
num_tpus = len([s for s in tpu_name_list if server_id in s])
print("Number of TPUs: %d" % num_tpus)


# Specify the LFADS data folder and filename (gs:// or local), PBT project name and output directory
name = 'lfadsRun'
run_save_path = 'gs://pbt-test-bucket-2/runs/'      # where PBT will store the runs
output_folder = 'gs://pbt-test-bucket-2/output/'    # where final PBT-LFADS output will be saved
data_dir = 'gs://pbt-test-bucket-2/data'            #  data folder
datafilename = 'lfads_datasset001.h5'

# use mounted directory for data folder
# bucket is mounted at /<bucket-name>/
if 'gs://' in data_dir:
    data_dir = data_dir[4:]

#lfads_output_dir = '/home/'+username+'/lfads'  # lfads
#zone = 'us-central1-f'

# Set PBT machine configuration

# command = "gcloud compute instance-groups managed list-instances group-{} --zone={} --format=\'value(NAME)\'".format(server_id, my_zone)
# vms = subprocess.check_output(command, shell=True)
# vms_list = vms.split(b'\n')[:-1]
#
# computers=[]
# keys = ['id', 'ip', 'max_processes', 'process_start_cmd', 'wait_for_process_start', 'zone']
# for vm in vms_list:
#     values = [vm, vm, '1', '/code/PBT_HP_opt/pbt_opt/run_lfads_client.sh', 'True', my_zone]
#     dictionary = dict(zip(keys, values))
#     computers.append(dictionary)


computers= [{'id':server_id,
            'ip':server_id,
            'max_processes':num_tpus,
            'process_start_cmd':'/code/PBT_HP_opt/pbt_opt/run_lfads_client.sh',
            'wait_for_process_start':True,
            'zone':my_zone}
            ]

# put the pbt run in the pbt_run folder
run_save_path = os.path.join(run_save_path, 'pbt_run/')


''' create server object '''

command = "gcloud --format=\"value(INTERNAL_IP)\" compute instances list --filter=\'name:%s\'" % server_id
server_ip = subprocess.check_output(command, shell=True)

svr = Server(name, run_save_path, num_workers=2, steps_to_ready=200,
             max_generations=2, exploit_method='binarytournament', exploit_param=[],
             explore_method='perturb', explore_param=0.8, mode='minimize', force_overwrite=True,
             mongo_server_ip=server_ip, port=27017, server_log_path=run_save_path, num_no_best_to_stop=3)


# add machines to be used by PBT
svr.add_computers(computers)

''' Specify the searchable parameters using explorable=True '''

# example if you want to use resample and specify the probablity of resampling per hyperparam
#resample_param = {'sample_mode':'rand',
#                  'sample_prob':0.5}

svr.add_hp('keep_prob', (0.6, 1.0), init_sample_mode='rand', explore_method='perturb', explore_param=0.3, limit_explore=True, explorable=True)

svr.add_hp('learning_rate_init', (0.0001, 0.05), init_sample_mode=[0.01], explore_method='perturb', explore_param=0.3,  explorable=True)


''' Search L2 penalties '''

svr.add_hp('l2_gen_scale', (0.1, 1000), init_sample_mode='logrand', explorable=True)
svr.add_hp('l2_ic_enc_scale', (0.1, 1000), init_sample_mode='logrand', explorable=True)

svr.add_hp('l2_con_scale', (0.1, 1000), init_sample_mode='logrand', explorable=True)
svr.add_hp('l2_ci_enc_scale', (0.1, 1000), init_sample_mode='logrand', explorable=True)

svr.add_hp('l2_gen_2_factors_scale', (0, 1000), init_sample_mode=[00.0], explorable=False)
svr.add_hp('l2_ci_enc_2_co_in', (0, 1000), init_sample_mode=[00.0], explorable=False)

# KL costs
svr.add_hp('kl_co_weight', (0.1, 5), init_sample_mode='logrand', explorable=True)
svr.add_hp('kl_ic_weight', (0.5, 2), init_sample_mode='logrand', explorable=True)


''' Path related params '''
svr.add_hp('data_dir', [data_dir], explorable=False)
svr.add_hp('data_filename_stem', [datafilename], explorable=False)


''' Other fixed params '''
svr.add_hp('keep_ratio', [0.7], explorable=False)
svr.add_hp('cd_grad_passthru_prob', [0.0], explorable=False)

svr.add_hp('max_ckpt_to_keep', [1], explorable=False)
svr.add_hp('max_ckpt_to_keep_lve', [1], explorable=False)
svr.add_hp('csv_log', ["fitlog"], explorable=False)
svr.add_hp('output_filename_stem', [""], explorable=False)
svr.add_hp('checkpoint_pb_load_name', ["checkpoint"], explorable=False)
svr.add_hp('checkpoint_name', ["lfads_vae"], explorable=False)
svr.add_hp('device', ["tpu"], explorable=False)
svr.add_hp('ps_nexamples_to_process', [100000000], explorable=False)


# important parameters
#svr.add_hp('val_cost_for_pbt', ['heldout_samp'], explorable=False)
svr.add_hp('val_cost_for_pbt', ['heldout_trial'], explorable=False)

svr.add_hp('cv_rand_seed', [1000], explorable=False)
svr.add_hp('cv_keep_ratio', [1.0], explorable=False)


svr.add_hp('factors_dim', [40], explorable=False)
svr.add_hp('in_factors_dim', [0])
svr.add_hp('do_train_readin', [False])
svr.add_hp('do_train_encoder_only', [False])
svr.add_hp('ext_input_dim', [0], explorable=False)

svr.add_hp('ic_dim', [64], explorable=False)
svr.add_hp('ic_enc_dim', [64], explorable=False)
svr.add_hp('gen_dim', [64], explorable=False)
#svr.add_hp('batch_size', [100], explorable=False)
svr.add_hp('allow_gpu_growth', [True], explorable=False)
svr.add_hp('learning_rate_decay_factor', [1], explorable=False)
svr.add_hp('learning_rate_stop', [1e-10], explorable=False)
svr.add_hp('learning_rate_n_to_compare', [0], explorable=False)
svr.add_hp('do_reset_learning_rate', [True], explorable=False)
svr.add_hp('con_ci_enc_in_dim', [10], explorable=False)
svr.add_hp('con_fac_in_dim', [10], explorable=False)
svr.add_hp('max_grad_norm', [200.0], explorable=False)
svr.add_hp('cell_clip_value', [5.0], explorable=False)
svr.add_hp('output_dist', ['poisson'], explorable=False)

svr.add_hp('co_dim', [2], explorable=False)
svr.add_hp('do_causal_controller', [False], explorable=False)
svr.add_hp('controller_input_lag', [1], explorable=False)
svr.add_hp('ci_enc_dim', [64], explorable=False)
svr.add_hp('con_dim', [64], explorable=False)

svr.add_hp('ic_prior_var', [0.1], explorable=False)
svr.add_hp('ic_post_var_min', [0.0001], explorable=False)
svr.add_hp('co_prior_var', [0.1], explorable=False)
svr.add_hp('co_post_var_min', [0.0001], explorable=False)
svr.add_hp('do_feed_factors_to_controller', [True], explorable=False)
svr.add_hp('feedback_factors_or_rates', ['factors'])
#svr.add_hp('l2_gen_scale', [500.0])
#svr.add_hp('l2_con_scale', [500.0])
svr.add_hp('temporal_spike_jitter_width', [0])
svr.add_hp('inject_ext_input_to_gen', [False])

svr.add_hp('kl_start_step', [-1])
svr.add_hp('l2_start_step', [-1])
svr.add_hp('kl_increase_steps', [1])
svr.add_hp('l2_increase_steps', [1])

svr.add_hp('train_batch_size', [800], explorable=False)
svr.add_hp('eval_batch_size', [240], explorable=False)

''' Start PBT '''
best_worker = svr.start_pbt()


''' get the path to the best worker '''
best_worker_path = best_worker.run_save_path

''' do posterior mean sample and average on the best model '''
# PM bach size
# pass None to use the training batch size (not recommended)
ps_repetitions = 100

# run posterior sample and average on the best worker
run_posterior_sample_and_average(best_worker_path, {'ps_repetitions': ps_repetitions})

''' copy the best worker to lfadsOutput for run-manager to load '''
copy_output(best_worker_path, output_folder)

