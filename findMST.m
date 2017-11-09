function [SP TREEMIN costcrude roots] = findMST(markedpaths, markedset)

% finds an arborescence (directed minimum weighted tree)
% does not require a root

% build the kxk (k:size of markedset) shortest paths matrix

k = length(markedset);

SP = zeros(k+1,k+1);

N = length(markedpaths);
SP(k+1, 1:k) = log2(N); % add the star/null node

for i=1:k
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

D = 1./SP;
D(D==Inf)=0;

V=(1:k+1)';
[i j w] = find(D);
E = [i j w];
GT= edmonds(V,E);
TREEMAX=reconstruct(GT);

unodes= unique([i;j]);
T = zeros(k+1,k+1);
T(unodes,unodes) = full(TREEMAX);
TREEMIN=SP.*logical(T);

%visualize arborescence
bg=visGraph(TREEMIN, [markedset 0], 1:k, 1, 1);
bg.view;

costcrude = full(sum(sum(TREEMIN)));

roots = find(TREEMIN(k+1,:)>0); %base-k
TREEMIN = TREEMIN(1:k,1:k);

%markedset(roots)
end