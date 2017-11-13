function [SP TREEMIN costcrude roots] = findMST3(markedpaths,markedset,markedset2,SP, TREEMIN)

% finds an arborescence (directed minimum weighted tree)
% does not require a root

% build the kxk (k:size of markedset) shortest paths matrix

k = length(markedset2);
m= length(SP);
SP2 = zeros(m+k,m+k); 
SP2(1:m-1,1:m-1)=SP(1:m-1,1:m-1);
SP=SP2;
N = length(markedpaths);
SP(m+k, 1:m+k-1) = log2(N); % add the star/null node

for i=1:k
    paths = markedpaths{markedset2(i)};
    if(isempty(paths))
        continue;
    end
    [u ind] = unique([paths.id],'first'); % first occurrence gives the shortest path
    costs = [paths.cost];
    
    for j=1:length(u)
        SP(([markedset markedset2] == u(j)),m+i-1) = costs(ind(j)); 
    end
end

D = 1./SP;
D(D==Inf)=0;

V = (1:k+m)';
[i j w] = find(D);
E = [i j w];
GT = edmonds(V,E);
TREEMAX = reconstruct(GT);

unodes= unique([i;j]);
T = zeros(m+k,m+k);
T(unodes,unodes) = full(TREEMAX);
TREEMIN=SP.*logical(T);

%visualize arborescence
bg=visGraph(TREEMIN, [markedset markedset2 0], 1:m+k-1, 1, 1);
bg.view;

costcrude = full(sum(sum(TREEMIN)));

roots = find(TREEMIN(m+k,:)>0); %base-k
TREEMIN = TREEMIN(1:m+k-1,1:m+k-1);

%markedset(roots)
end