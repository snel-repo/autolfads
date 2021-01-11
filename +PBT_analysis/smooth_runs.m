function runs = smooth_runs( runs, varstosmooth, smoothlevel )

if ~iscell(varstosmooth)
    varstosmooth = {varstosmooth};
end
    
%%
for nv = 1:numel(varstosmooth)
    vartosmooth = varstosmooth{nv};
    for igen = 1 : size( runs, 1 )

        for iworker = 1 : size( runs, 2 )
            data = runs( igen, iworker ).( vartosmooth );
            data = smooth( data, smoothlevel );
            runs( igen, iworker ).( vartosmooth ) = data;
        end
    end
end
