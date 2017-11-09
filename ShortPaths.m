function [markedpaths] = ShortPaths2( W, logdeg, markedset )

% similar to ShortPaths, but also stores the paths to unmarked vertices
% from marked vertices, i.e. markedpaths is larger

% Input:
% an undirected, unweighted graph + indices/ids of marked nodes
% converts the graph into weighted
% prunes degree 1 unmarked nodes, iteratively
% finds multiple short paths in increasing length between marked nodes

%Output:
% markedpaths: cell array of structs 
% W: weighted adjacency matrix by logdegorg
% logdegorg: log2(deg+1)


TIMES = 1; %TIMESxlog2(N) length paths will be found

N = size(W,1);


% adjecency list format will be faster
marked = sparse(N,1);
marked(markedset) = 1;

markedpaths = cell(N,1); 

MAXLEN = log2(N)*TIMES;

for i=1:length(markedset)
    
    %tic
    hops=0;
    seed = markedset(i);
    costseed = logdeg(seed);
    hops = hops + costseed; % jump to level-1 neighbors directly (same cost)
    
   
    
    ids = [];
    costs = [];
    paths = {};
    
    % initially add all neighbors to the "paths" queue
    neighs = find(W(seed,:)>0);    
    for j=1:length(neighs)
        path = seed;
        path = [path neighs(j)];
        ids = [ids; neighs(j)];
        costs = [costs; logdeg(neighs(j))];
        paths{end+1} = path;
        
        % add to neighbor's path-list
        markedpaths=add_markedpath(markedpaths, neighs(j), seed, hops, path);
        
    end
    
    % find the minimum cost in level-hop paths
    mincost = min(costs);
    % subtract min-cost from all
    costs = costs - mincost;
    % increase hops by min-cost
    hops = hops + mincost;
    
    while(hops<=MAXLEN)
        % expand those that hit zero --
        ind = find(costs==0);
        %length(ind)
        for j=1:length(ind) %---------------------------------------
        % -- add expand nodes' neighbors to levelhoppaths
        % -- if expands to marked node, add to its markedpaths
            expandnode = ids(ind(j));
            neighs = find(W(expandnode,:)>0);
            
            for k=1:length(neighs)
                path = paths{ind(j)};
                
                % if neighbor already in path, continue
                int = find(path == neighs(k));
                if(length(int)>0)
                   continue; 
                end
                % otherwise expand
                path = [path neighs(k)];
                ids = [ids; neighs(k)];
                costs = [costs; logdeg(neighs(k))];
                paths{end+1} = path;

                % add to neighbor's path-list
                markedpaths=add_markedpath(markedpaths, neighs(k), seed, hops, path);
                
            end
        end
        
        % remove expand nodes
        ids(ind)=[];
        costs(ind)=[];
        paths(ind)=[];
        
        
        % find the minimum cost in levelhop-paths
        mincost = min(costs);
        % subtract min-cost from all
        costs = costs - mincost;
        % increase hops by min-cost
        hops = hops + mincost;
        
        %if(mincost<=0.0001 && hops>=(MAXLEN/TIMES+2) )
        %    break;
        %end
       %[num2str(i),'       ',num2str(hops)]
        
    end
    %toc
    
  
end



% -----  Utility functions  -----

function paths = add_markedpath (path0, id, ...
                            from, ...
                            cost, ...
                            path)
    paths = path0;
    if(length(paths{id}) ==0 )
        paths{id} = ...
        struct('id', from, ...
               'cost', cost, ...
               'path', path);
    else
        paths{id}(end+1) = ...
        struct('id', from, ...
               'cost', cost, ...
               'path', path);
    end
    
    return
end


end

