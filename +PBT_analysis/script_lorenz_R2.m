%% need to add the PBT_HP_opt directory and its utils directory
%addpath( '~/snelhome/projects/PBT_HP_opt/PBT_HP_opt' );
%addpath( '~/snelhome/projects/PBT_HP_opt/PBT_HP_opt/utils' );

%% save directory
rname = 'pbt_r2';
savedir = fullfile('/snel/share/runs/PBT/results/', rname);
if ~exist(savedir, 'file')
    mkdir(savedir)
end
%% load all the pbt results
testdir = '/snel/share/runs/PBT/lorenz_spike/pbt_R2_lorenz';
benchmark = '/snel/share/runs/PBT/lorenz_spike/standard/lfadsliteOutputL2_gen_ic_1000/fitlog.csv';
benchmark_names = {
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
ylims = [900 1700];
opacity = 0.2;
%epoch_per_gen = 25;


figure(1); clf;
set(gcf, 'color', [1 1 1]);
ah(1) = Plot.subtightplot(2,1,1, marg_xy, marg_h, marg_w);
hold on
ah(2) = Plot.subtightplot(2,1,2, marg_xy, marg_h, marg_w);
hold on
%% plot baseline runs
for d = benchmark_names
    % overlay benchmark runs
    benchmark = sprintf('/snel/share/runs/PBT/lorenz_spike/standard/%s/fitlog.csv', d{1});
    log = PBT_analysis.read_fitlog( benchmark );
    epoch = cellfun(@(x) str2num(x), log(:, 2) );
    train = cellfun(@(x) str2num(x), log(:, 9) );
    valid = cellfun(@(x) str2num(x), log(:, 10) );
    axes(ah(1))
    h = plot((epoch+epoch_per_gen)/epoch_per_gen, train, 'k');
    %set(h, 'edgealpha', opacity, 'facealpha', opacity);
    %alpha(opacity)
    axes(ah(2))
    h=plot((epoch+epoch_per_gen)/epoch_per_gen, valid, 'k');
    %set(h, 'edgealpha', opacity, 'facealpha', opacity);
    %set(h, 'edgealpha', opacity, 'facealpha', opacity);
    alpha(opacity)
end


%% plot pbt runs
axes(ah(1));
PBT_analysis.plot_pbt_results( runs, 'train', opacity );
axis('tight')
ylim( ylims )
ylabel('train cost');
xlabel('generation');

axes(ah(2));
PBT_analysis.plot_pbt_results( runs, 'valid', opacity );
axis('tight')
ylim( ylims )
ylabel('valid cost');
xlabel('generation');

set(ah, 'fontsize', 6);
linkaxes(ah)
%%
export_fig(fullfile(savedir, [rname  '_cost.png']))
export_fig(fullfile(savedir, [rname  '_cost.fig']))

%% Plot R^2
marg_xy = [0.02 0.04];
marg_h = [0.07 0.05];
marg_w = [0.1 0.01];
ylims = [0.5 1.0];
opacity = 0.2;

figure(2); clf;
set(gcf, 'color', [1 1 1]);
ah(1) = Plot.subtightplot(2,1,1, marg_xy, marg_h, marg_w);
hold on
ah(2) = Plot.subtightplot(2,1,2, marg_xy, marg_h, marg_w);
hold on

axes(ah(1));
PBT_analysis.plot_pbt_results( runs, 'r2_heldin', opacity );
axis('tight')
ylim( ylims )
ylabel('held-in samples');
xlabel('generation');

axes(ah(2));
PBT_analysis.plot_pbt_results( runs, 'r2_heldout', opacity );
axis('tight')
ylim( ylims )
ylabel('held_out samples');
xlabel('generation');

set(ah, 'fontsize', 6);
linkaxes(ah)

%%
%export_fig(fullfile(savedir, [rname  '.pdf']))
export_fig(fullfile(savedir, [rname  '_r2.png']))
export_fig(fullfile(savedir, [rname  '_r2.fig']))

%%
%hp_list = {'learning_rate_init', 'l2_gen_2_factors_scale', 'l2_gen_scale', 'l2_ic_enc_scale', };
hp_list = {'learning_rate_init', 'l2_gen_scale', 'l2_ci_enc_scale', 'l2_con_scale', 'kl_co_weight', 'l2_ic_enc_scale' };
for hp = hp_list
    figure; clf;
    set(gcf, 'color', [1 1 1]);
    ah2 = Plot.subtightplot(1,1,1, 0.05, [0.09 0.06], [0.08 0.01]);
    PBT_analysis.plot_pbt_results( runs, hp{1}, opacity );
    set(gca, 'yscale', 'log')
    axis('tight')
    ylabel(hp{1}, 'Interpreter', 'none');
    xlabel('generation');
    set(ah2, 'fontsize', 8);
    title(hp{1}, 'Interpreter', 'none', 'FontSize', 12)
    %export_fig(fullfile(savedir, [rname  hp{1} '.pdf']))
    export_fig(fullfile(savedir, [rname '_' hp{1} '.png']))
    export_fig(fullfile(savedir, [rname '_' hp{1} '.fig']))
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
