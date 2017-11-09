function [L2MIN treenodes roots] = localUpdates(uallnodes, L1MIN, markedpaths, markedset, roots, logdeg)
% uallnodes: all the nodes in candidate graph (base-N)
% L1MIN: kxk (forest of) minimum level-1 tree(s)
% markedpaths: cell-array of path structs
% markedset: list of IDs of marked nodes
% roots: indices of roots in L1MIN (base-k)
% logdeg: Nx1 log2(deg+1) for all the nodes
%Output:
% roots: indices of roots in L2MIN (base-|treenodes|)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% takes a level-1 tree and tries to expand it to a level-2 tree %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
N = length(markedpaths);

% start with kxk level-1 tree(s), 0's for no-edge
L2MIN = L1MIN;
% initially, tree nodes consist of all the marked nodes
treenodes = markedset;

% actual root ids
rootsid = markedset(roots);


% for each roots level-1 tree, expand to level-2 separately
for i=1:length(roots)
    % find nodes that belong to root-i's level-1 tree
    leafix = find(L1MIN(roots(i),:)>0); % (base-k)
    leafs = markedset(leafix); % actual leaf IDs, all leaf nodes are marked nodes
    
    
    if(length(leafs)<2) 
        continue;
    end
    
    r = rootsid(i); % actual ID
    
    while(1) %%%%%%%%%%%%%%%%%%%% while there are leaf nodes not covered
      
    maxsavings = 0; % 1.savings (want negative)
    maxv = inf; % 2.intermediary-node ID with best savings
    maxleafind = []; % 3.indices of leaf nodes covered by v (base-k)
    
    % for all nodes v in the candidate graph (except root-i)
    V = length(uallnodes);
    
    for j=1:V
        v = uallnodes(j);
        
        if(v==r)
            continue;
        end
        %1. find the distance from r to v
        paths = markedpaths{v};
        if(length(paths)==0) % if no path from r to v
            continue;
        end
        ind = find([paths.id] == r);   
        if(length(ind)==0) % if no path from r to v
            continue;
        end
        
        
        %sp = paths(ind(1)).path;
        
        cvr = paths(ind(1)).cost; % first occurrence gives the shortest path
        
        % find the costs from v to leafs-of-r (all marked)
        leafcosts = inf(1,length(leafs)); % inf if no path from v
        for t=1:length(leafs)
            ind = find([paths.id] == leafs(t));
            if(length(ind)==0) % no path from v to leafs(t)
                continue;
            end
            %sp = paths(ind(1)).path;
            
            leafcosts(t) = paths(ind(1)).cost - logdeg(leafs(t)) + logdeg(v);            
        end
        
        
        
        if(sum(leafcosts~=inf) < 2) % v needs to connect to at least 2 leaf nodes for savings
            continue; % try another v
        end
        
        %2. connect v to leaf w/ minimum cost
        [c1 ind1] = min(leafcosts);        
        savings = cvr + c1 - L1MIN(roots(i), leafix(ind1)); % is >= 0
        leafcosts(ind1) = inf;
        
        %3. sort vertices by l1mincost - ci in decreasing order
        diff = L1MIN(roots(i),leafix)-leafcosts; % positive and negative values and -inf
        
        
        
        %4. subtract the positive ones (also not -inf)
        ind = find(diff>=0);
        if(length(ind)==0) % if no positive-savings path exists
            continue; % try another v
        end
        
        savings = savings - sum(diff(ind)); % want negative savings        
        %pause
        if(savings < maxsavings)
            
            % add v to L2MIN
            
            n = length(treenodes);
            
            mind = find(treenodes==v);
            if(length(mind)==0)
                L2MINt = zeros(n+1,n+1); %n+1 is v
                L2MINt(1:n,1:n) = L2MIN;
                subtreecost = 0;
                L2MINt(roots(i), end) = cvr; 
                subtreecost = subtreecost + cvr;
                L2MINt(roots(i), leafix(ind1)) = 0; %remove link to first leaf
                L2MINt(end, leafix(ind1)) = c1;
                subtreecost = subtreecost + c1;
                for t=1:length(ind)
                    L2MINt(roots(i), leafix(ind(t))) = 0; %remove link to other leaf nodes
                    L2MINt(end, leafix(ind(t))) = leafcosts(ind(t));
                    subtreecost = subtreecost + leafcosts(ind(t));
                end
            else                
                L2MINt = L2MIN;
                subtreecost = 0;
                L2MINt(roots(i), mind) = cvr; 
                subtreecost = subtreecost + cvr;
                L2MINt(roots(i), leafix(ind1)) = 0; %remove link to first leaf
                L2MINt(mind, leafix(ind1)) = c1;
                subtreecost = subtreecost + c1;
                for t=1:length(ind)
                    L2MINt(roots(i), leafix(ind(t))) = 0; %remove link to other leaf nodes
                    L2MINt(mind, leafix(ind(t))) = leafcosts(ind(t));
                    subtreecost = subtreecost + leafcosts(ind(t));
                end
                
            end
            % CHECK! if average cost is less than log2(N)
            
            
            avgcost = subtreecost / (length(ind)+1); % +1 for ind1 leaf node     
            if(avgcost <= log2(N))         
                maxsavings = savings; %1
                maxv = v; %2    
                maxleafind = [ind1 ind]; %3
            else
                %fprintf('Avg. cost of subtree leafs %f\n', avgcost);
            end
            %assert(maxsavings == ( sum(sum(L2MINt)) - sum(sum(L2MIN)) ))
        end
        
    end % trying v's
    
    if(maxsavings < 0)
        %fprintf('Max savings achieved for v: %d for %f bits \n', maxv, maxsavings);
        % find if it is a marked node
        if(length(find(treenodes==maxv))==0)
            treenodes = [treenodes maxv];            
        end
        L2MIN = L2MINt;
        leafix(maxleafind) = []; % remove covered leaf nodes 
        leafs = markedset(leafix); % actual ID's of remaining uncovered leaf nodes
        
        
        if(length(leafs) < 2) % if less than 2 leaf nodes left
            break;
        end
    else
        break; % no v reduces cost
    end
    
    end % while (for uncovered leaf nodes)
    
end


% Remove edges with cost greater than log2N, 
%%%% if it is between two marked nodes
k=length(markedset);
lg = L2MIN(1:k,1:k)<=log2(N);
L2MIN(1:k,1:k) = L2MIN(1:k,1:k) .* lg;

% Find roots==nodes with indegree zero
indeg = sum(L2MIN,1);
roots = find(indeg==0);



end


