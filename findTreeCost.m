function cost = findTreeCost( TREEMIN, markedset, roots, deg )

% TREEMIN: NxN matrix for found 'minimum' tree (expanded, i.e. contains marked and unmarked nodes) 
% marked nodes: (base-N)
% roots: root nodes in TREEMIN (base-N)
% deg: Nx1 degree array of all nodes


warning('off')

N = size(TREEMIN,1);
numparts = length(roots);

% 1. transmit the number of partitions |P|: L(|P|) = log |V| (worst case |V| partitions)
%log2(N)
cost = log2(N);

% 2. identify root nodes for all trees in one go (since they do not
% overlap): log (|V| choose |P|)
%log2(nchoosek(N, numparts))
cost = cost + log2(nchoosek(N, numparts));

% 3. per partition p in P, there exists a tree T
for i=1:numparts
    % 2.1 per node t in T
    nodes = findTreeNodes(roots(i));
    %pause
    sizeT = length(nodes);
    for t=1:sizeT
        % 2.1.1 transmit number of branches of node t
        bnodes = find(TREEMIN(nodes(t),:)>0);
        cost = cost + logstar2(length(bnodes));
        % 2.1.2 identify which out-edges/branches of node t will be visited
        %log2(nchoosek(deg(nodes(t)), sum(TREEMIN(nodes(t),:)>0)))
        cost = cost + log2(nchoosek(deg(nodes(t)), length(bnodes)));
        % 2.1.3 \sum_j^|t| L(b(t,j)): identify node t' in T you reach from
        % t in T via descending branch j ??? <--- Jilles
        %pause
    end    
    % 2.2 identify the marked nodes in T
        % 2.2.1 transmit number of marked nodes ||T|| < T
        % log2(sizeT)
        cost = cost + log2(sizeT);
        % 2.2.2 identify which ||T|| nodes of T are marked
        markedt = intersect(markedset, nodes);
        %log2(nchoosek(sizeT, length(markedt)))
        cost = cost + log2(nchoosek(sizeT, length(markedt)));
        %pause
end



function nodes = findTreeNodes(root)
    nodes = root;
    toexpand = root;
    while(length(toexpand)>0)
        ind = find(TREEMIN(toexpand(1),:)>0); 
        nodes = [nodes ind];
        toexpand = [toexpand ind];
        toexpand(1) = [];
    end
end

function l = logstar2(n)
% LOGSTAR2  return log-star (universal integer code length) of n
%
% $Id: logstar2.m,v 1.2 2004/02/04 23:56:17 spapadim Exp $
    l = 0;
    n = log2(n);
    while n > 0
      l = l + n;
      n = log2(n);
    end
    l = l + log2(2.8665064);
end



end

