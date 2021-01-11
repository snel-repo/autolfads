classdef RunCollection < LFADS.RunCollection
    % no need to modify anything here, but feel free to add useful methods
    % and properties as useful
    
    methods
        function rc = RunCollection(rootPath, name, datasetCollection, varargin)
            rc@LFADS.RunCollection(rootPath, name, datasetCollection, varargin{:});
        end
        
        % write PBT run shell script
        function writePBTShellScript(rc)
            % write shell script for PBT run
            for r = rc.runs(:)'
                if r.params.doPBT
                    run_dir = r.path;
                    data_dir = r.pathLFADSInput;
                    lfads_output = r.pathLFADSOutput;
                    pbt_run_name = [rc.name '_' r.name];
                    shell_str = sprintf('python %s %s %s %s %s', r.params.PBTscript, pbt_run_name, run_dir, data_dir, lfads_output);
                    pbt_script = fullfile(run_dir, 'run_pbt_script.sh');
                    fid = fopen(pbt_script, 'w+');
                    fprintf(fid, shell_str);
                    fclose(fid);
                    r.params.fileShellScriptPBTTrain = pbt_script;
                end
            end
        end
    end
end