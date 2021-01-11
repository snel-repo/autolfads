

r2_func = @(a,b) corrcoef(a,b).^2;

%% load true data
%in_fname = '/snel/share/runs/PBT/lorenz_spike/data/lfads_dataset001.h5';
%indata = PBT_analysis.load_h5_data(in_fname);
data1 = load('/snel/share/data/lfads_lorenz/dataset001.mat');

l_traj = data1.lorenz_trajectories;
% Extract relevant trial parameters
nTrials = size(data1.conditionId,1);
nConds = size(l_traj,3);
nTpC = nTrials/nConds;
trialLength = size(l_traj,2);

s = zeros(3,nTrials*trialLength);

for i=1:nConds
    tmp = repmat(l_traj(:,:,i),1,nTpC);
    s(:,(i-1)*size(tmp,2)+1:i*size(tmp,2)) = tmp;
end
%Down-sample s to match lfads data sample rate
res = 5;
s = s(:,1:res:end);
s = reshape(s, size(s,1), trialLength/res, nTrials);
t_rates = data1.true_rates;%, [2,3,1]);
[Tr, D, SS] = size(t_rates);
t_rates = reshape(t_rates, Tr, D, res, []);
t_rates = squeeze(sum(t_rates, 3));
t_rates = permute(t_rates, [2,3,1]);

spikes = data1.spikes;
spikes = reshape(spikes, Tr, D, res, []);
spikes = squeeze(sum(spikes, 3));
spikes = permute(spikes, [2,3,1]);

%% load lfads output data

% coordinated dropout
%data_file = '/snel/share/runs/PBT/lorenz_spike/data/lfads_dataset001.h5'; 
%data_file = '/snel/share/runs/PBT/paper/data/lfads_dataset001.h5';
data_file = '/snel/share/data/lfads_lorenz/lfads_dataset001.h5';
%PM_file = '/snel/share/runs/PBT/lorenz_spike/standard/lfadsliteOutput_R2_test/dataset001.h5_valid_posterior_sample_and_average';
%PM_file = '/snel/share/runs/PBT/paper/standard/LFADSOutput_noinp/model_runs_dataset001.h5_valid_posterior_sample_and_average';
%PM_file = '/snel/share/runs/PBT/paper/standard/LFADSOutput_20ms_noinp/model_runs_dataset001.h5_train_posterior_sample_and_average';
PM_file = '/snel/share/runs/tpu_test/runs-model_runs_dataset001.h5_valid_posterior_sample_and_average';
%PM_file = '/snel/share/runs/dev_runs/tfdata/lfadsliteOutput/model_runs_dataset001.h5_valid_posterior_sample_and_average'; 
%PM_file = '/snel/share/runs/float16/loss_sweep/32_loss_scale_1_Reza_1/model_runs_dataset001.h5_valid_posterior_sample_and_average';
%PM_file = '/snel/share/runs/float16/loss_sweep/32_loss_scale_1_Reza_mean5/model_runs_dataset001.h5_valid_posterior_sample_and_average';
% standard dropout co_dim=2
%PM_file = '/snel/share/runs/PBT/lorenz_spike/pbt_inputs_bench/g019_w05/model_runs_dataset001.h5_valid_posterior_sample_and_average';
% no inputs
%PM_file = '/snel/share/runs/PBT/lorenz_spike/test_l2_gen_ic_enc_40_smth_2/g047_w30/model_runs_dataset001.h5_valid_posterior_sample_and_average';

pm_data = PBT_analysis.load_h5_data(PM_file);
in_data = PBT_analysis.load_h5_data(data_file);

x_rates = in_data.valid_truth / in_data.conversion_factor;
x = s(:,:,1:5:end); % get only validation trials
x_rates = t_rates(:,:,1:5:end);
%x = x(:,:,1:5:end)=[]; % get only train trials


y = pm_data.factors;
y_rates = pm_data.output_dist_params;

x_l = reshape(x, size(x,1), []);
y_l = reshape(y, size(y,1), []);

W = y_l' \ x_l';

x_p = W' * y_l  ;

r2 = r2_func(x_p(1,:), x_l(1,:)); r2 = r2(2);
r2_rates = r2_func(y_rates, x_rates); r2_rates = r2_rates(2);

fprintf(1, 'Factors R^2: %g\n', r2)
fprintf(1, 'Rates R^2: %g\n', r2_rates)

%% plot lorenz states
chan_vec = [1 2 3];
trial_vec = [1, 10, 20, 50, 100];
figure
%subplot(length(chan_vec), lenght(trial_vec), 1)

marg_h = [0.02 0.02];
marg_w = [0.01 0.01];
marg_xy = [0.01 0.01];
opacity = 0.2;

i = 0;
for c = chan_vec
    for t = trial_vec
        i = i + 1;
        ah(1) = Plot.subtightplot(length(chan_vec), length(trial_vec), i, marg_xy, marg_h, marg_w);
        set(gca,'YTickLabel',[]);
        %set(gca,'XTickLabel',[]);
        hold on
        plot(x(c, :, t))
        yp = W' * y(:, :, t);
        plot(yp(c, :))
    end
end

%% plot rates
chan_vec = [1 15 25];
trial_vec = [1, 10, 20, 50, 100];
figure
%subplot(length(chan_vec), lenght(trial_vec), 1)

marg_h = [0.02 0.02];
marg_w = [0.01 0.01];
marg_xy = [0.01 0.01];
opacity = 0.2;

i = 0;
for c = chan_vec
    for t = trial_vec
        i = i + 1;
        ah(1) = Plot.subtightplot(length(chan_vec), length(trial_vec), i, marg_xy, marg_h, marg_w);
        set(gca,'YTickLabel',[]);
        %set(gca,'XTickLabel',[]);
        hold on
        plot(x_rates(c, :, t))
        plot(y_rates(c, :, t))
    end
end

%% plots inputs
figure
i = 0;
marg_h = [0.02 0.02];
marg_w = [0.01 0.01];
marg_xy = [0.05 0.05];
opacity = 0.2;
yl = [-0.05 0.05];
for t = trial_vec
    i = i + 1;
    Plot.subtightplot(1, length(trial_vec), i, marg_xy, marg_h, marg_w);
    hold on
    %set(gca,'YTickLabel',[]);
    set(gca,'XTickLabel',[]);
    ylim(yl)
    plot(squeeze(pm_data.controller_outputs(:, :, t))')
end


firing rates