
ogle cloud related parameters used in shell scripts to set up cloud infrastructure

# Shell scripts
1. server_name - Name of the server VM. Used in the server_set_up.sh script
2. zone - zone in which the VM will be created. Used for both - server and the client VMs. Used in the server_set_up.sh and machine_setup.sh scripts
3. client_name - The root name of the client VM created when you call machine_setup.sh script. When you create 3 client VMs with client_name set to "clvm", the client machines are named clvm1, clvm2 clvm3. Note that this is different from the tag name. Used in the machine_setup.sh script
4. number_of_clients - Number of client machines created when you call the machine_setup.sh script. Each client VM has a single GPU
5. name_of_GPU - The GPU used with each client machine. The default GPU is nvidia-tesla-k80

tagname - this is the common alias of all client VMs. Helps in cases when a given command is needed to be run on all client VMs. We have set the tagname to "pbtclient" and this need not be changed




#### PBT PARAMS

# pbt script

1. bucket_name - Name of the cloud bucket
2. data_path - data directory inside the cloud bucket
3. run_path - run directory inside the cloud bucket
4. nprocess_gpu - Number of processes to be run on each GPU

# Server Object
1. epochs_per_generation - Number of epochs per each generation
2. max_generations - Maximum number of generations. It may actually take lesser generations to converge to the best model, depending on the converging criterion defined in 'num_no_best_to_stop' and 'min_change_to_stop'
3. explore_method - The method used to explore hyper-parameters. Accepts two possible arguments - 'perturb' and 'resample'
4. explore_param - The parameters for the explore method defined by the 'explore_method' arg. When the 'explore_method' is set to 'perturb', the explore_param takes in a scalar between 0 and 1. A random number is then sampled uniformly from (1-explore_parama, 1+explore_param). This sampled number is then used as a factor which is multiplied to the HPs current value to perturb it. When the 'explore_method' is set to 'resample', the 'explore_param' must be set to None. In this condition, the new value of the HP is then obtained by resampling from a range of values defined for that parameter (Defined in the 'add_hp' method)
5. mongo_server_ip : The ip address of the VM on which mongo DB is running. By default, the mongo DB runs on the server and the ip address of the server is passed her
6. port : The port on which mongo DB runs (on the machine identified by mongo_server_ip)
7. server_log_path - The path where the server generated log files are stored. Not advised to change this parameter
8. num_no_best_to_stop : If no improvement is seen in the best worker for these many successive generations, PBT is terminated even before the max_generations are completed
9. min_change_to_stop : If the improvement in the best worker over successive generations is less than this quantity, the improvement is considered to be 0. Default value is 0.0005 (or .05 percentage ). If the num_no_best_to_stop is set to 5 and min_change_to_stop is set to 0.0005 , the PBT training will terminate if for 5 successive generations the improvement in the best worker is less than 0.05% over the previous best worker
10. docker_name : The name of the docker container. By default set to "docker_pbt" in the pbt_helper_fn.py

details for the add_hp method

name : name of the HP
value - uses tuple to indicate range, or list/nparray for allowable values
init_sample_mode: 'rand','logrand' or 'grid', mode of preferred initialization. Or pass 
explorable: True or False, whether the 'explore' action should apply to this hyperparameter
explore_method : Same as the 'explore_method' defined for the Server class. The value of the 'explore_method' defined for the Server class is the default 'explore_method' for all HPs. However this value can be overwritten by passing it again for the specific HP.
explore_param : Same as the 'explore_param' defined for the Server class. This can be overwritten for a specific HP just like explore_method
limit_explore : If True, the new value of the HP after applying the explore method, cannot exceed the range defined by the "value" arg. 


#### LFADS

keep_prob - Dropout keep probability
keep_ratio - coordinated dropout input keep probability
l2_gen_scale - L2 regularization cost for the generator
l2_ic_enc_scale - L2 regularization cost for the initial condition encoder
l2_con_scale - L2 cost for the controller
l2_ci_enc_scale - L2 cost for the controller input encoder
kl_co_weight - Strength of KL weight on controller output KL penalty
kl_ic_weight - Strength of KL weight on initial conditions KL penalty
do_calc_r2 - Calculate R^2 if the truth rates are available
cell_clip_value - Max value recurrent cell can take before being clipped
prior_ar_atau - Initial autocorrelation of AR(1) priors. This param is not searched often
prior_ar_nvar - Initial noise variance for AR(1) priors. This param is not searched often
ckpt_save_interval - Number of epochs between saving (non-lve) checkpoints. Doesn't has to be searched
do_train_prior_ar_atau - Determines whether the value for atau is trainable, or not. Boolean
do_train_prior_ar_nvar - Determines whether the value for noise variance is trainable, or not. Boolean
kl_start_epoch - Start increasing KL weight after these many epochs
l2_start_epoch - Start increasing l2 weight after these many epochs
kl_increase_epochs - Increase KL weight for these many epochs
l2_increase_epochs - Increase l2 weight for these many epochs
batch_size - batch_size to use during training
valid_batch_size - batch_size to use during validation
val_cost_for_pbt - Set to either held-out samples ("heldout_samp") or heldout trials ("heldout_trial"). Validation cost is computed over these
cv_keep_ratio - Cross-validation keep probability. Ratio of samples kept for training in the train set - if set to 80%, then 20% of samples from the training set are used for sample validation
cd_grad_passthru_prob - Probability of passing through gradients in coordinated dropout. Allows some percentage of gradients to backpropagate - if set to 0.1 , then 10% of gradients which were supposed to be blocked, are actually passed through
factors_dim - Number of factors from the generator
ic_enc_dim - dimension of hidden state of the initial condition encoder
ic_enc_seg_len - Segment length passed to initial condition encoder for causal modeling. Set to 0 (default)
gen_dim - size of hidden state for generator
co_dim - dimensionality of the inferred inputs by the controller
ci_enc_dim - size of the hidden state in the controller encoder
con_dim - "Cell hidden size, controller" - hidden state of the controller
do_causal_controller - Restrict the controller to infer only causal inputs. Boolean
output_dist - spikes are modeled as observations of underlying rates, modeled as this distribution. Default - 'poisson'
learning_rate_decay_factor - Learning rate decay, decay by this fraction (How frequently is the decay applied)
learning_rate_stop - stop training when the learning rate reaches this value
learning_rate_n_to_compare - The current cost has to be less than these many previous costs to lower learning rate
checkpoint_pb_load_name - Name of checkpoint files. Default - 'checkpoint'
loss_scale - scaling of loss
adam_epsilon - Epsilon parameter for Adam optimizer
beta1 - beta1 parameter for Adam optimizer
beta2 - beta2 parameter for Adam optimizer
data_filename_stem - prefix for the data filename (h5 file)
data_dir - directory of the data h5 file
do_train_readin - Whether to train the read-in matrices and bias vectors. Boolean. False - leave them fixed at their initial values specified by the alignment matrices and vectors
do_train_encoder_only - Train only the encoder weights
cv_rand_seed - Random seed for held-out cross-validation sample mask
output_filename_stem - Name of output file (postfix will be added)
max_ckpt_to_keep - Max number of checkpoints to keep (keeps that many latest checkpoints)
max_ckpt_to_keep_lve - Max number of checkpoints to keep for lowest validation error models (keeps that many lowest validation error checkpoints)
csv_log - Name of file to keep the log of fit likelihoods (.csv appended to name)
checkpoint_name - Name of checkpoint files (.ckpt appended)
device - which device to use (GPU/CPU). By default set to GPU.
ps_nexamples_to_process - Number of examples to process for posterior sample and average (not number of samples to average over)
ic_prior_var - Minimum variance of IC prior distribution
ic_post_var_min - Minimum variance of IC posterior distribution
co_prior_var - Variance of controller input prior distribution
do_feed_factors_to_controller - Should the controller network receive the feedback from the factors. Boolean. Should be set to True
temporal_spike_jitter_width - jitters the spike, adds temporal noise during training. Avoids overfitting individual spikes
inject_ext_input_to_gen - Inject the external input to the generator (Boolean). Should be set to True
allow_gpu_growth - If true, only allocate the amount of memory needed for Session. Otherwise, use full GPU memory. Boolean
max_grad_norm - Maximum norm of gradient before gradient clipping is applied
do_reset_learning_rate - Reset the learning rate to initial value from the provided HP (HP - 'learning_rate_init'). Should be set to True


