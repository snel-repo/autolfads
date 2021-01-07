<h2>Shell Scripts</h2>

<table>
<thead>
<th>Name</th>
<th>Description</th>
</thead>

<tbody class="hp">


<tr class="hp-rare">
<td>server_name</td>
<td>Name of the server VM. Used in the server_set_up.sh script</td>
</tr>
<tr class="hp-rare">
<td>zone</td>
<td>Zone in which the VM will be created. Used for both - server and the client VMs. Used in the server_set_up.sh and machine_setup.sh scripts</td>
</tr>
<tr class="hp-rare">
<td>client_name</td>
<td>The root name of the client VM created when you call machine_setup.sh script. When you create 3 client VMs with client_name set to "clvm", the client machines are named clvm1, clvm2 clvm3. Note that this is different from the tag name. Used in the machine_setup.sh script</td>
</tr>
<tr class="hp-rare">
<td>number_of_clients</td>
<td>Number of client machines created when you call the machine_setup.sh script. Each client VM has a single GPU</td>
</tr>
<tr class="hp-rare">
<td>name_of_GPU</td>
<td>The GPU used with each client machine. The default GPU is nvidia-tesla-k80</td>
</tr>
</tbody>
<tr class="hp-rare">
<td>tag name</td>
<td>This is the common alias of all client VMs. Helps in cases when a given command is needed to be run on all client VMs. We have set the tagname to "pbtclient" and this need not be changed</td>

<table>
<thead>
<th>Name</th>
<th>Description</th>
</thead>

<h2>PBT Script</h2>

<tbody class="hp">

<tr class="hp-rare">
<td>num_workers</td>
<td>Number of workers in the population</td>
</tr>

<tr class="hp-rare">
<td>steps_to_ready</td>
<td>Number of training steps until member of population pauses training and is ready to exploit and explore</td>
</tr>

<tr class="hp-rare">
<td>bucket_name</td>
<td>Name of the cloud bucket</td>
</tr>
<tr class="hp-rare">
<td>data_path</td>
<td>data directory inside the cloud bucket</td>
</tr>
<tr class="hp-rare">
<td>run_path</td>
<td>Run directory inside the cloud bucket</td>
</tr>
<tr class="hp-rare">
<td>nprocess_gpu</td>
<td>Number of processes to be run on each GPU</td>
</tr>

</tbody>
</table>

<h2>Server Object</h2>

<table>
<thead>
<th>Name</th>
<th>Description</th>
</thead>


<tr class="hp-rare">
<td>epochs_per_generation</td>
<td>Number of epochs per each generation</td>
</tr>
<tr class="hp-rare">
<td>max_generations</td>
<td>Maximum number of generations. It may actually take lesser generations to converge to the best model, depending on the converging criterion defined in 'num_no_best_to_stop' and 'min_change_to_stop'</td>
</tr>
<tr class="hp-rare">
<td>explore_method</td>
<td>The method used to explore hyper-parameters. Accepts two possible arguments - 'perturb' and 'resample'</td>
</tr>
<tr class="hp-rare">
<td>explore_param</td>
<td>The parameters for the explore method defined by the 'explore_method' arg. When the 'explore_method' is set to 'perturb', the explore_param takes in a scalar between 0 and 1. A random number is then sampled uniformly from (1-explore_parama, 1+explore_param). This sampled number is then used as a factor which is multiplied to the HPs current value to perturb it. When the 'explore_method' is set to 'resample', the 'explore_param' must be set to None. In this condition, the new value of the HP is then obtained by resampling from a range of values defined for that parameter (Defined in the 'add_hp' method)</td>
</tr>
<tr class="hp-rare">
<td>mongo_server_ip</td>
<td>The ip address of the VM on which mongo DB is running. By default, the mongo DB runs on the server and the ip address of the server is passed her</td>
</tr>
<tr class="hp-rare">
<td>port</td>
<td>The port on which mongo DB runs (on the machine identified by mongo_server_ip)</td>
</tr>
<tr class="hp-rare">
<td>server_log_path</td>
<td>The path where the server generated log files are stored. Not advised to change this parameter</td>
</tr>
<tr class="hp-rare">
<td>num_no_best_to_stop</td>
<td>If no improvement is seen in the best worker for these many successive generations, PBT is terminated even before the max_generations are completed</td>
</tr>
<tr class="hp-rare">
<td>min_change_to_stop</td>
<td>If the improvement in the best worker over successive generations is less than this quantity, the improvement is considered to be 0. Default value is 0.0005 (or .05 percentage ). If the num_no_best_to_stop is set to 5 and min_change_to_stop is set to 0.0005 , the PBT training will terminate if for 5 successive generations the improvement in the best worker is less than 0.05% over the previous best worker</td>
</tr>
<tr class="hp-rare">
<td>docker_name</td>
<td>The name of the docker container. By default set to "docker_pbt" in the pbt_helper_fn.py</td>
</tr>

</tbody>
</table>

<h2>Details For The <code>Add_hp</code> method

<table>
<thead>
<th>Name</th>
<th>Description</th>
</thead>

<tr class="hp-rare">
<td>name</td>
<td>Name of the HP</td>
</tr>
<tr class="hp-rare">
<td>value</td>
<td>Uses tuple to indicate range, or list/nparray for allowable values</td>
</tr>
<tr class="hp-rare">
<td>init_sample_mode</td>
<td>'Rand','logrand' or 'grid', mode of preferred initialization. Or pass </td>
</tr>
<tr class="hp-rare">
<td>explorable</td>
<td>True or False, whether the 'explore' action should apply to this hyperparameter</td>
</tr>
<tr class="hp-rare">
<td>explore_method</td>
<td>Same as the 'explore_method' defined for the Server class. The value of the 'explore_method' defined for the Server class is the default 'explore_method' for all HPs. However this value can be overwritten by passing it again for the specific HP.</td>
</tr>
<tr class="hp-rare">
<td>explore_param</td>
<td>Same as the 'explore_param' defined for the Server class. This can be overwritten for a specific HP just like explore_method</td>
</tr>
<tr class="hp-rare">
<td>limit_explore</td>
<td>If true, the new value of the HP after applying the explore method, cannot exceed the range defined by the "value" arg. </td>
</tr>

</tbody>
</table>

<h2>LFADS</h2>

<table>
<thead>
<th>Name</th>
<th>Description</th>
</thead>

<tr class="hp-rare">
<td>keep_prob</td>
<td>Dropout keep probability</td>
</tr>
<tr class="hp-rare">
<td>keep_ratio</td>
<td>Coordinated dropout input keep probability</td>
</tr>
<tr class="hp-rare">
<td>l2_gen_scale</td>
<td>L2 regularization cost for the generator</td>
</tr>
<tr class="hp-rare">
<td>l2_ic_enc_scale</td>
<td>L2 regularization cost for the initial condition encoder</td>
</tr>
<tr class="hp-rare">
<td>l2_con_scale</td>
<td>L2 cost for the controller</td>
</tr>
<tr class="hp-rare">
<td>l2_ci_enc_scale</td>
<td>L2 cost for the controller input encoder</td>
</tr>
<tr class="hp-rare">
<td>kl_co_weight</td>
<td>Strength of KL weight on controller output KL penalty</td>
</tr>
<tr class="hp-rare">
<td>kl_ic_weight</td>
<td>Strength of KL weight on initial conditions KL penalty</td>
</tr>
<tr class="hp-rare">
<td>do_calc_r2</td>
<td>Calculate R^2 if the truth rates are available</td>
</tr>
<tr class="hp-rare">
<td>cell_clip_value</td>
<td>Max value recurrent cell can take before being clipped</td>
</tr>
<tr class="hp-rare">
<td>prior_ar_atau</td>
<td>Initial autocorrelation of AR(1) priors. This param is not searched often</td>
</tr>
<tr class="hp-rare">
<td>prior_ar_nvar</td>
<td>Initial noise variance for AR(1) priors. This param is not searched often</td>
</tr>
<tr class="hp-rare">
<td>ckpt_save_interval</td>
<td>Number of epochs between saving (non-lve) checkpoints. Doesn't has to be searched</td>
</tr>
<tr class="hp-rare">
<td>do_train_prior_ar_atau</td>
<td>Determines whether the value for atau is trainable, or not. Boolean</td>
</tr>
<tr class="hp-rare">
<td>do_train_prior_ar_nvar</td>
<td>Determines whether the value for noise variance is trainable, or not. Boolean</td>
</tr>
<tr class="hp-rare">
<td>kl_start_epoch</td>
<td>Start increasing KL weight after these many epochs</td>
</tr>
<tr class="hp-rare">
<td>l2_start_epoch</td>
<td>Start increasing l2 weight after these many epochs</td>
</tr>
<tr class="hp-rare">
<td>kl_increase_epochs</td>
<td>Increase KL weight for these many epochs</td>
</tr>
<tr class="hp-rare">
<td>l2_increase_epochs</td>
<td>Increase l2 weight for these many epochs</td>
</tr>
<tr class="hp-rare">
<td>batch_size</td>
<td>Batch_size to use during training</td>
</tr>
<tr class="hp-rare">
<td>valid_batch_size</td>
<td>Batch_size to use during validation</td>
</tr>
<tr class="hp-rare">
<td>val_cost_for_pbt</td>
<td>Set to either held-out samples ("heldout_samp") or heldout trials ("heldout_trial"). Validation cost is computed over these</td>
</tr>
<tr class="hp-rare">
<td>cv_keep_ratio</td>
<td>Cross-validation keep probability. Ratio of samples kept for training in the train set - if set to 80%, then 20% of samples from the training set are used for sample validation</td>
</tr>
<tr class="hp-rare">
<td>cd_grad_passthru_prob</td>
<td>Probability of passing through gradients in coordinated dropout. Allows some percentage of gradients to backpropagate - if set to 0.1 , then 10% of gradients which were supposed to be blocked, are actually passed through</td>
</tr>
<tr class="hp-rare">
<td>factors_dim</td>
<td>Number of factors from the generator</td>
</tr>
<tr class="hp-rare">
<td>ic_enc_dim</td>
<td>Dimension of hidden state of the initial condition encoder</td>
</tr>
<tr class="hp-rare">
<td>ic_enc_seg_len</td>
<td>Segment length passed to initial condition encoder for causal modeling. Set to 0 (default)</td>
</tr>
<tr class="hp-rare">
<td>gen_dim</td>
<td>Size of hidden state for generator</td>
</tr>
<tr class="hp-rare">
<td>co_dim</td>
<td>Dimensionality of the inferred inputs by the controller</td>
</tr>
<tr class="hp-rare">
<td>ci_enc_dim</td>
<td>Size of the hidden state in the controller encoder</td>
</tr>
<tr class="hp-rare">
<td>con_dim</td>
<td>"Cell hidden size, controller" - hidden state of the controller</td>
</tr>
<tr class="hp-rare">
<td>do_causal_controller</td>
<td>Restrict the controller to infer only causal inputs. Boolean</td>
</tr>
<tr class="hp-rare">
<td>output_dist</td>
<td>Spikes are modeled as observations of underlying rates, modeled as this distribution. Default - 'poisson'</td>
</tr>
<tr class="hp-rare">
<td>learning_rate_decay_factor</td>
<td>Learning rate decay, decay by this fraction (How frequently is the decay applied)</td>
</tr>
<tr class="hp-rare">
<td>learning_rate_stop</td>
<td>Stop training when the learning rate reaches this value</td>
</tr>
<tr class="hp-rare">
<td>learning_rate_n_to_compare</td>
<td>The current cost has to be less than these many previous costs to lower learning rate</td>
</tr>
<tr class="hp-rare">
<td>checkpoint_pb_load_name</td>
<td>Name of checkpoint files. Default - 'checkpoint'</td>
</tr>
<tr class="hp-rare">
<td>loss_scale</td>
<td>Scaling of loss</td>
</tr>
<tr class="hp-rare">
<td>adam_epsilon</td>
<td>Epsilon parameter for Adam optimizer</td>
</tr>
<tr class="hp-rare">
<td>beta1</td>
<td>Beta1 parameter for Adam optimizer</td>
</tr>
<tr class="hp-rare">
<td>beta2</td>
<td>Beta2 parameter for Adam optimizer</td>
</tr>
<tr class="hp-rare">
<td>data_filename_stem</td>
<td>Prefix for the data filename (h5 file)</td>
</tr>
<tr class="hp-rare">
<td>data_dir</td>
<td>Directory of the data h5 file</td>
</tr>
<tr class="hp-rare">
<td>do_train_readin</td>
<td>Whether to train the read-in matrices and bias vectors. Boolean. False - leave them fixed at their initial values specified by the alignment matrices and vectors</td>
</tr>
<tr class="hp-rare">
<td>do_train_encoder_only</td>
<td>Train only the encoder weights</td>
</tr>
<tr class="hp-rare">
<td>cv_rand_seed</td>
<td>Random seed for held-out cross-validation sample mask</td>
</tr>
<tr class="hp-rare">
<td>output_filename_stem</td>
<td>Name of output file (postfix will be added)</td>
</tr>
<tr class="hp-rare">
<td>max_ckpt_to_keep</td>
<td>Max number of checkpoints to keep (keeps that many latest checkpoints)</td>
</tr>
<tr class="hp-rare">
<td>max_ckpt_to_keep_lve</td>
<td>Max number of checkpoints to keep for lowest validation error models (keeps that many lowest validation error checkpoints)</td>
</tr>
<tr class="hp-rare">
<td>csv_log</td>
<td>Name of file to keep the log of fit likelihoods (.csv appended to name)</td>
</tr>
<tr class="hp-rare">
<td>checkpoint_name</td>
<td>Name of checkpoint files (.ckpt appended)</td>
</tr>
<tr class="hp-rare">
<td>device</td>
<td>Which device to use (GPU/CPU). By default set to GPU.</td>
</tr>
<tr class="hp-rare">
<td>ps_nexamples_to_process</td>
<td>Number of examples to process for posterior sample and average (not number of samples to average over)</td>
</tr>
<tr class="hp-rare">
<td>ic_prior_var</td>
<td>Minimum variance of IC prior distribution</td>
</tr>
<tr class="hp-rare">
<td>ic_post_var_min</td>
<td>Minimum variance of IC posterior distribution</td>
</tr>
<tr class="hp-rare">
<td>co_prior_var</td>
<td>Variance of controller input prior distribution</td>
</tr>
<tr class="hp-rare">
<td>do_feed_factors_to_controller</td>
<td>Should the controller network receive the feedback from the factors. Boolean. Should be set to True</td>
</tr>
<tr class="hp-rare">
<td>temporal_spike_jitter_width</td>
<td>Jitters the spike, adds temporal noise during training. Avoids overfitting individual spikes</td>
</tr>
<tr class="hp-rare">
<td>inject_ext_input_to_gen</td>
<td>Inject the external input to the generator (Boolean). Should be set to True</td>
</tr>
<tr class="hp-rare">
<td>allow_gpu_growth</td>
<td>If true, only allocate the amount of memory needed for Session. Otherwise, use full GPU memory. Boolean</td>
</tr>
<tr class="hp-rare">
<td>max_grad_norm</td>
<td>Maximum norm of gradient before gradient clipping is applied</td>
</tr>
<tr class="hp-rare">
<td>do_reset_learning_rate</td>
<td>Reset the learning rate to initial value from the provided HP (HP - 'learning_rate_init'). Should be set to True</td>
</tr>

</tbody>
</table>
