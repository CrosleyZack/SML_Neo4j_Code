function [SP L1MINP minrootsp mincost] = findMinLevel1(markedpaths, markedset, W, deg, level)
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



% find actual level-1 tree
SP2=SP;
SP2(SP2>log2(N))=inf;

% if(level==1 && size(SP2,1)>1)
% SPv = SP2;
% SPv(SPv==inf)=0;
% bg=visGraph(SPv, markedset, 1:k, 1, 1);
% bg.view;
% clear SPv;
% end

% find the cost for each marked node as root
mincost = inf;
%L1MINP = zeros(k,k);
%minrootsp = [];
for i=1:k
        
    %disp('root')
    %markedset(i)
    %pause
    reached = zeros(1,k);    
    roots = i;
    reached(i) = 1;
    reached(SP2(i,:)>0 & SP2(i,:)~=inf) = 1;
    
    SPL1 = zeros(k,k);
    SPL1(i,:) = SP2(i,:);
    SPL1(SPL1==inf)=0;
    ix = find(reached==0);
    l1min = zeros(length(ix),length(ix));
    if(sum(reached)<k)       
       %r = ix(1);
       %disp('self')
       %markedset(ix)
       %pause
       [trash, l1min, rootsp, trash] = findMinLevel1(markedpaths, markedset(ix), W, deg, level+1);
       
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
         [trash, PMIN, trash, trash, trash] = expandPathsAll(SP, SPL1, markedpaths, markedset, markedset, W, 0);
         cost = findTreeCost( PMIN, markedset, markedset(roots), deg );
         
         if(cost < mincost)
           mincost = cost;
           L1MINP = SPL1;
           minrootsp = roots;
         end
         
         %markedset(roots)
         %cost
%         pause
     else    
        cost = rcost * length(roots);
        cost = cost + sum(sum(SPL1));
        if(cost < mincost)
           mincost = cost;
           L1MINP = SPL1;
           minrootsp = roots;
        end
     end
end
%L1MINP

% if(level==1 && size(L1MINP,1)>1)
% bg=visGraph(L1MINP, markedset, 1:k, 1, 1);
% bg.view;
% markedset(minrootsp)
% mincost
% 
% end

%numroots = length(roots)







end