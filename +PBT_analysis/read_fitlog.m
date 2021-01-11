function [values, column_names_map] = read_fitlog(filename)
    column_names = {'epoch', 'step', 'total_train', 'total_valid', ...
        'recon_train', 'recon_train_samp', 'recon_valid', 'recon_valid_samp', ...
        'r2_train', 'r2_train_heldout', 'r2_valid', 'r2_valid_heldout', 'kl_train', 'kl_valid', 'l2',...
        'klweight', 'l2weight', 'lr'};
    inds = [2, 4, 6,7, 9,10,11,12, 15,16,17,18, 20, 21, 23, 25, 27, 29];
    formatstr = '';
    for i = 1:max(inds)
        if any(inds==i)
            formatstr = [formatstr  '%f'];
        else
            formatstr = [formatstr  '%*s'];
        end
    end

    fh = fopen(filename ,'r');
    % read formatted file directly
    values = textscan(fh, formatstr, 'Delimiter', ',', 'CollectOutput',1);
    values = values{1};
    fclose(fh);
    
    column_names_map = containers.Map(column_names, 1:numel(column_names));
