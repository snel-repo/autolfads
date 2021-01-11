%% need to add the PBT_HP_opt directory and its utils directory
addpath( '/snel/home/mreza/projects/PBT_HP_opt/PBT_HP_opt' );
addpath( '/snel/home/mreza/projects/PBT_HP_opt/PBT_HP_opt/utils' );

%% save directory

% PBT run name (folder name)
run_name = 'pbt_oldValid_dropout';
%run_name = 'pbt_oldValid_logresample_all';

res_name = 'perich_long_dropout_lfadslite_base';

savedir = fullfile('/snel/home/mreza/results/Perich/PBT/perich_long_noCorr/', res_name);
if ~exist(savedir, 'file')
    mkdir(savedir)
end

%% load all the pbt results
% get the PBT run folder name
testdir = sprintf('/snel/share/runs/PBT/perich/perich_long_noCorr/%s/', run_name);
%benchmark = '/snel/share/runs/PBT/perich/perich_long_noCorr/baseline_coord/fitlog.csv';
%benchmark = '/snel/share/runs/PBT/perich/perich_short_noCorr/baseline_coord/fitlog.csv';

% what type of baseline rrun LFADS or lfadslite? (for plotting purpose)
baseline_type = 'lfadslite';

% lfadslite benchmarks (CD on)
% short data
%benchmark_names = {'/snel/share/runs/PBT/perich/perich_short_noCorr/baselines/lfadslite/Run1', ...
%    '/snel/share/runs/PBT/perich/perich_short_noCorr/baselines/lfadslite/Run2', ...
%    '/snel/share/runs/PBT/perich/perich_short_noCorr/baselines/lfadslite/Run3', ...
%    '/snel/share/runs/PBT/perich/perich_short_noCorr/baselines/lfadslite/Run4'    
%    };

% LFADS benchmarks
% short data
%benchmark_names = {'/snel/share/runs/PBT/perich/perich_short_noCorr/baselines/LFADS/Run1', ...
%    '/snel/share/runs/PBT/perich/perich_short_noCorr/baselines/LFADS/Run2', ...
%    '/snel/share/runs/PBT/perich/perich_short_noCorr/baselines/LFADS/Run3', ...
%    '/snel/share/runs/PBT/perich/perich_short_noCorr/baselines/LFADS/Run4'
%};

% LFADS benchmarks
% long data
%benchmark_names = {'/snel/share/runs/PBT/perich/perich_long_noCorr/baselines/LFADS/Run1', ...
%    '/snel/share/runs/PBT/perich/perich_long_noCorr/baselines/LFADS/Run2', ...
%    '/snel/share/runs/PBT/perich/perich_long_noCorr/baselines/LFADS/Run3', ...
%    '/snel/share/runs/PBT/perich/perich_long_noCorr/baselines/LFADS/Run4'
%};

% lfadslite benchmarks (CD on)
% long data
benchmark_names = {
    '/snel/share/runs/PBT/perich/perich_long_noCorr/baselines/lfadslite/Run1', ...
    '/snel/share/runs/PBT/perich/perich_long_noCorr/baselines/lfadslite/Run2', ...
    '/snel/share/runs/PBT/perich/perich_long_noCorr/baselines/lfadslite/Run3', ...
    '/snel/share/runs/PBT/perich/perich_long_noCorr/baselines/lfadslite/Run4'    
    };

%%
%testdir = '/snel/share/runs/PBT/lorenz_spike/test_pbt_lr_dropout/';
[runs, epoch_per_gen] = PBT_analysis.load_pbt_results( testdir );
epoch_per_gen

%% smooth the data a bit
%smoothlevel = 10;
%runs = PBT_analysis.smooth_runs( runs, { 'train', 'valid' }, smoothlevel );

%% plot some
marg_xy = [0.02 0.04];
marg_h = [0.07 0.05];
marg_w = [0.1 0.01];

idx = cellfun(@(x) length(x), {runs.valid});
idx = idx == epoch_per_gen;
%ylims = [1100 2000];
v = [runs(idx).valid]; v = v(:);
tr = [runs(idx).train]; tr = tr(:);
ylims = [mean(tr) - 0.2*std(tr), mean(v) + 0.3*std(v)];

opacity = 0.9;

%
figure(1); clf;
set(gcf, 'color', [1 1 1]);
ah(1) = Plot.subtightplot(2,1,1, marg_xy, marg_h, marg_w);
hold on
ah(2) = Plot.subtightplot(2,1,2, marg_xy, marg_h, marg_w);
hold on
%ah(3) = Plot.subtightplot(3,1,3, marg_xy, marg_h, marg_w);
%hold on

%% PBT results
axes(ah(1));
PBT_analysis.plot_pbt_results( runs, 'train', opacity );

ylabel('train cost');
xlabel('generation');




axes(ah(2));
PBT_analysis.plot_pbt_results( runs, 'valid', opacity );
%axis('tight')
%ylim( ylims )
ylabel('valid trial cost');
xlabel('generation');

linkaxes(ah)
set(ah, 'fontsize', 10);

%axis('tight')
ylim( ylims )
xlim([1 size(runs,1)])

%% plot valid samp
axes(ah(3));
PBT_analysis.plot_pbt_results( runs, 'valid_samp', opacity );
axis('tight')
ylim( ylims )
ylabel('valid samp cost');
xlabel('generation');

linkaxes(ah)
set(ah, 'fontsize', 10);
%%
num_benchmarks = numel(benchmark_names);
colmap = lines(num_benchmarks);

for i = 1:num_benchmarks 
    % overlay benchmark runs
    benchmark = sprintf('%s/fitlog.csv', benchmark_names{i});
    log = PBT_analysis.read_fitlog( benchmark );
    
    
    %epoch = cellfun(@(x) str2num(x), log(:, 2) );
    
    train = cellfun(@(x) str2num(x), log(:, 9) );
    epoch = 1:length(train);
    if strcmp(baseline_type, 'LFADS')    
        % this is for LFADS log file
        valid = cellfun(@(x) str2num(x), log(:, 10) );   
    else
        % this is for lfadslite log file
        valid = cellfun(@(x) str2num(x), log(:, 11) );
    end

    
    axes(ah(1))
    h = plot((epoch+epoch_per_gen)/epoch_per_gen, train, 'Color', colmap(i, :), 'LineWidth', 0.5);
    %set(h, 'edgealpha', opacity, 'facealpha', opacity);
    %alpha(opacity)
    axes(ah(2))
    h=plot((epoch+epoch_per_gen)/epoch_per_gen, valid, 'Color', colmap(i, :), 'LineWidth', 0.5);
    %set(h, 'edgealpha', opacity, 'facealpha', opacity);
    %set(h, 'edgealpha', opacity, 'facealpha', opacity);
    alpha(opacity)
end


%%
%export_fig(fullfile(savedir, [rname  '.pdf']))
saveas(gcf, fullfile(savedir, res_name),  'png');
%export_fig(fullfile(savedir, [rname  '.png']))

%export_fig(fullfile(savedir, [rname  '.fig']))

%%
%hp_list = {'learning_rate_init', 'l2_gen_2_factors_scale', 'l2_gen_scale', 'l2_ic_enc_scale', };
opacity = 0.95;
hp_list = {'keep_prob', 'learning_rate_init', 'l2_gen_scale', 'l2_ic_enc_scale', 'l2_ci_enc_scale', 'l2_con_scale', 'kl_co_weight', 'kl_ic_weight' };
hp_list = {'keep_prob', 'kl_co_weight'};
for hp = hp_list
    figure; clf;
    set(gcf, 'color', [1 1 1]);
    ah2 = Plot.subtightplot(1,1,1, 0.05, [0.12 0.1], [0.12 0.05]);
    PBT_analysis.plot_pbt_results( runs, hp{1}, opacity );
    set(gca, 'yscale', 'log')
    axis('tight')
    %ylabel(hp{1}, 'Interpreter', 'none');
    xlabel('Generation');
    set(ah2, 'fontsize', 12);
    %title(hp{1}, 'Interpreter', 'none', 'FontSize', 12)
    %export_fig(fullfile(savedir, [rname  hp{1} '.pdf']))
    %saveas(gcf, fullfile(savedir, [res_name '_' hp{1}]),  'png');
    xlim([1 15])
    print('-dpng', '-r500', fullfile(savedir, [res_name '_' hp{1}]));
    %export_fig(fullfile(savedir, [rname '_' hp{1} '.png']))
    %export_fig(fullfile(savedir, [rname '_' hp{1} '.fig']))
end


%%
% figure(3); clf;
% set(gcf, 'color', [1 1 1]);
% ah2 = Plot.subtightplot(1,1,1, 0.05, [0.06 0.01], [0.045 0.01]);
% PBT_analysis.plot_pbt_results( runs, 'keep_prob', opacity );
% axis('tight')
% ylabel('learning rate');
% xlabel('generation');
% set(ah2, 'fontsize', 6);
