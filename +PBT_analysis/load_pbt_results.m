function [runs, epochs_per_gen] = load_pbt_results( pbtdir, read_hps )

s = what('PBT_analysis');
s = s.path;
addpath(fullfile(s, 'utils'));


if ~exist('read_hps')
    read_hps = false;
end
%%
contents = dir( pbtdir );
% only keep directories, and things that aren't named '.' or '..'
contents = contents( [ contents.isdir ] );
alldirs = { contents.name };
exclude = { '.', '..' };
keep = true( size( contents ) );
[~, ia, ib] = intersect( alldirs, exclude );
keep( ia ) = false;
contents = contents( keep );

%%
runs = [];
alldirs = { contents.name };
prog = PBT_analysis.ProgressBar( numel( alldirs ), 'Loading info');
max_gen = [];
max_worker = [];
all_values = cell(1, numel( alldirs ));
parfor ndir = 1 : numel( alldirs )
    % read the log
    thislog = fullfile( pbtdir, alldirs{ ndir }, 'fitlog_smoothed.csv' );
    % backward compatibility
    if ~exist(thislog, 'file')
        thislog = fullfile( pbtdir, alldirs{ ndir }, 'fitlog.csv' );
    end
    
    try 
        [all_values{ndir}, columns{ndir}] = PBT_analysis.read_fitlog( thislog );
    catch
        warning('could not read log file %s', thislog);
        continue
    end
    runinfo = sscanf( alldirs{ ndir }, 'g%g_w%g');
    max_gen = [max_gen, runinfo( 1 )];
    max_worker = [max_worker, runinfo( 2 ) + 1];
end

max_gen = max(max_gen);
max_worker = max(max_worker);
columns = columns{1};

epoch_count = numel(alldirs);
runs(max_gen, max_worker).epoch = 0;
runs( max_gen, max_worker ).epoch = 0;
runs( max_gen, max_worker ).valid = 0;
runs( max_gen, max_worker ).valid_samp = 0;
runs( max_gen, max_worker ).train = 0;
runs( max_gen, max_worker ).r2_heldin = 0;
runs( max_gen, max_worker ).r2_heldout = 0;
runs( max_gen, max_worker ).r2_valid_heldin = 0;
runs( max_gen, max_worker ).r2_valid_heldout = 0;
runs( max_gen, max_worker ).l2_weight = 0;
    
for ndir = 1 : numel( alldirs )
    prog.update(ndir, 'Loading info for run %s', alldirs{ ndir });
    %thislog = fullfile( pbtdir, alldirs{ ndir }, 'fitlog.csv' );
    %try 
    %    [values, columns] = PBT_analysis.read_fitlog( thislog );
    %catch
    %    warning('could not read log file %s', thislog);
    %    continue
    %end
    values = all_values{ndir};
    %log = all_log{ndir};
    %epoch_count(ndir) = size(values,1);
    % store down info about this run
    runinfo = sscanf( alldirs{ ndir }, 'g%g_w%g');
    gen = runinfo( 1 );
    worker = runinfo( 2 ) + 1; % these are 0-indexed
    if isempty(values), continue; end
    runs( gen, worker ).epoch = values(:, columns('epoch'));
    runs( gen, worker ).valid = values(:, columns('recon_valid'));
    runs( gen, worker ).valid_samp = values(:, columns('recon_train_samp'));
    runs( gen, worker ).train = values(:, columns('recon_train'));
    runs( gen, worker ).r2_heldin = values(:, columns('r2_train'));
    runs( gen, worker ).r2_heldout = values(:, columns('r2_train_heldout'));
    runs( gen, worker ).r2_valid_heldin = values(:, columns('r2_valid'));
    runs( gen, worker ).r2_valid_heldout = values(:, columns('r2_valid_heldout'));
    runs( gen, worker ).l2_weight = values(:, columns('l2weight'));
    
    % find the hyperparameters file
    if read_hps
        %try
            hpsfile = dir( fullfile( pbtdir, alldirs{ ndir }, 'hyperparameters-*.txt' ) );
            hpsfile = fullfile( pbtdir, alldirs{ ndir }, hpsfile(1).name );
            s = warning('off', 'MATLAB:namelengthmaxexceeded');

            % json files sometimes have errors that need to be fixed
            jsonstring = fileread( hpsfile );
            jsonstring = PBT_analysis.escape_bad_json( jsonstring );

            runs( gen, worker ).hps = jsonlab.loadjson( jsonstring );
        %catch
        %    runs( gen, worker ).hps = [];
        %end
    end
end
prog.finish();
epochs_per_gen = epoch_count(1);
