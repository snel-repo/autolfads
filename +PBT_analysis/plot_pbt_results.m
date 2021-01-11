function plot_pbt_results( runs, vartoplot, opacity )
%%
plotindex = 0;
startpoint = 0;
colorOrder = get(gca, 'ColorOrder');

if ~exist('opacity', 'var')
    opacity = 0.5;
end

for igen = 1 : size( runs, 1 )
    % get max epoch number
    allEpochs = arrayfun( @(x) max( x.epoch ), runs( igen, : ), ...
                          'uniformoutput', false);
    maxepoch = length( vertcat( allEpochs{ : } ) );

    for iworker = 1 : size( runs, 2 )
        % skip things that didn't actually run yet
        if isempty( runs( igen, iworker ).epoch )
            continue;
        end
        plotindex = plotindex + 1;
        %color = [0,1,1]; %colorOrder( mod( plotindex, size(colorOrder, 1))+1, :);
        color = colorOrder( mod( plotindex, size(colorOrder, 1))+1, :);
        switch vartoplot
          case {'valid', 'valid_samp', 'train'}
            epochs = runs( igen, iworker ).epoch;
            epochs = epochs - epochs(1);
            gs = igen  +  epochs/ maxepoch;
            data = runs( igen, iworker ).( vartoplot );
            h = Plot.patchline(gs, ...
                               data);
            set(h, 'edgealpha', opacity, 'facealpha', opacity);
            set(h, 'edgecolor', color, 'facecolor', color);
            set(h, 'linewidth', 1.1);
          
          case {'r2_heldin', 'r2_heldout'}
            epochs = runs( igen, iworker ).epoch;
            epochs = epochs - epochs(1);
            gs = igen  +  epochs/ maxepoch;
            data = runs( igen, iworker ).( vartoplot );
            h = Plot.patchline(gs, ...
                               data );
            set(h, 'edgealpha', opacity, 'facealpha', opacity);
            set(h, 'edgecolor', color, 'facecolor', color);  
            set(h, 'linewidth', 1.1);
          case {'learning_rate_init', 'keep_prob'}
              try
            data = runs( igen, iworker ).hps.( vartoplot );
            thisrand(1) = 0.1 * ( rand(1,1)-0.5);
            thisrand(2) = 0.01 * ( rand(1,1)-0.5);
            % add some y-variability to keep prob
            %   to separate overlapping pts
            if strcmp( vartoplot, 'keep_prob' )
                data = data + thisrand(2);
            else
                data = data * (1 + thisrand(2) );
            end
            h = scatter( igen + thisrand( 1 ), ...
                         data , '.' );
            set( h, 'markerfacealpha', opacity );
            set( h, 'markeredgealpha', opacity );
            set( h, 'sizedata', 170 );
              end
          otherwise
           try
            data = runs( igen, iworker ).hps.( vartoplot );
            thisrand(1) = 0.1 * ( rand(1,1)-0.5);
            thisrand(2) = 0.01 * ( rand(1,1)-0.5);
            % add some y-variability to keep prob
            %   to separate overlapping pts
            data = data * (1 + thisrand(2) );
            h = scatter( igen + thisrand( 1 ), ...
                         data , '.' );
            set( h, 'markerfacealpha', opacity );
            set( h, 'markeredgealpha', opacity );
            set( h, 'sizedata', 170 );                
                
                %disp( 'huh?' );
           end
        end
        hold on;
    end
end
set(gca, 'xgrid', 'on' );
%set(gca, 'ygrid', 'on' );
