function [SP minSPL1 minrootsL1 minL2MIN mintreenodes minrootsL2 mincostL2 mincostNaive mincostTJ] = findMinLevel2(markedpaths, markedset, W, deg,level, istest)
% minSPL1: L1MIN including >log2N weights
% L1MINP: original min level-1 tree 

% build the kxk (k:size of markedset) shortest paths matrix

k = length(markedset);

SP = inf(k,k); % holds the from-to shortest paths

N = length(markedpaths);
rcost = log2(N); %cost of a new root

for i=1:k
    SP(i,i) = 0;
    
    paths = markedpaths{markedset(i)};
    if(isempty(paths))
        continue;
    end
    [u ind] = unique([paths.id],'first'); % first occurrence gives the shortest path
    costs = [paths.cost];
    for j=1:length(u)
        SP((markedset == u(j)),i) = costs(ind(j)); 
    end
end

% if(size(SP,1)>1 && level==1)
% SPv = SP;
% SPv(SPv==inf)=0;
% bg=visGraph(SPv, markedset, 1:k, 1, 1);
% bg.view;
% end

% find the cost for each marked node as root
mincostL2 = inf;
mincostNaive=inf;
mincostTJ=inf;
for i=1:k
    reached = zeros(1,k);    
    roots = i;
    reached(i) = 1;
    reached(SP(i,:)>0 & SP(i,:)~=inf) = 1;
    
    
    SPL1 = zeros(k,k);
    SPL1(i,:) = SP(i,:);
    SPL1(SPL1==inf)=0;    
    ix = find(reached==0);
    l1min = zeros(length(ix),length(ix));
    if(sum(reached)<k)  
        
       %r = ix(1);
       %disp('self')
       %markedset(ix)
       %pause
       [trash, l1min, rootsp, trash, trash, trash, trash, trash, trash] = findMinLevel2(markedpaths, markedset(ix), W, deg, level+1, istest);
       
       %roots = [roots r];
       roots = [roots ix(rootsp)];
       %reached(r) = 1;
       %reached(SP2(r,:)>0 & SP2(r,:)~=inf) = 1;
    end
    
    % now, roots contains the root nodes
    
    SPL1(ix,ix) = l1min;
%     % assign each marked node to the root closest to it
%     SPL1 = zeros(k,k);
%     for j=1:k
%         if(sum(roots==j)>0)
%             continue;
%         end
%         [m ind] = min(SP2(roots,j));
%         SPL1(roots(ind),j) = m;
%     end
    
    
    
    if(level==1)
        %SPL1
%         if(size(SPL1,1)>1)
%            bg=visGraph(SPL1, markedset, 1:k, 1, 1);
%            bg.view;
%         end
        % roots
   
        [trash, trash, uallnodes, trash, trash] = expandPathsAll(SP, SPL1, markedpaths, markedset, markedset, W, 0);
       
        if(istest)
            [L2MIN treenodes rootsL2] = localUpdatesTest(uallnodes, SPL1, markedpaths, markedset, roots, log2(deg+1));
        else
            [L2MIN treenodes rootsL2] = localUpdates(uallnodes, SPL1, markedpaths, markedset, roots, log2(deg+1));
        end
        %L2MIN
        % L2MIN can be greater than kxk due to additional intermediary nodes,
        % rootsL2: base-size(L2MIN,1)
        [trash, PMIN trash, trash, cost] = expandPathsAll(SP, L2MIN, markedpaths, treenodes, markedset, W, 0);
        cost =  cost+length(rootsL2)*rcost;
        %PMIN
        %treenodes(rootsL2)
        %pause
        costT = findTreeCost( PMIN, markedset, treenodes(rootsL2), deg );
        %costTJ = findTreeCostJ( PMIN, markedset, treenodes(rootsL2), deg );
        
        if(costT < mincostL2)
           mincostL2 = costT;    
           mincostNaive = cost;
           %mincostTJ = costTJ;
           minL2MIN = L2MIN;
           mintreenodes = treenodes;
           minrootsL2 = rootsL2;
           
           minSPL1 = SPL1;
           minrootsL1 = roots;

        end
    else
        cost = rcost * length(roots);
        cost = cost + sum(sum(SPL1));
        if(cost < mincostL2)    
           mincostL2 = cost;
           minrootsL1 = roots;
           minSPL1 = SPL1;
           minL2MIN = []; 
           mintreenodes = [];
           minrootsL2 = [];
           mincostNaive = inf;
           %mincostTJ = inf;
        end
    end
end







end