function [ PMIN, roots, cost ] = findConnCompT( W, markedset )

addpath('edmonds')

k=length(markedset);
N=size(W,1);

T1 = zeros(k+1, k+1);
T1(1:k,1:k) = W(markedset,markedset); 
T1(k+1, 1:k) = log2(N); % add the star/null node
% T1 has reciprocal links, might not be a tree (eg. triangle)
% find min spanning tree out of it
D = 1./T1;
D(D==Inf)=0;

V=(1:k+1)';
[i j w] = find(D);
E = [i j w];
GT= edmonds(V,E);
TREEMAX=reconstruct_2(GT);

unodes= unique([i;j]);
T = zeros(k+1,k+1);
T(unodes,unodes) = full(TREEMAX);
TREEMIN=T1.*logical(T);
clear T1; clear TREEMAX; clear T; clear GT; clear E; clear D;

roots = find(TREEMIN(k+1,:)>0); % base-k
TREEMIN = TREEMIN(1:k,1:k);


PMIN = sparse(N,N);
PMIN(markedset,markedset) = TREEMIN;

cost = full(sum(sum(PMIN)));
cost = cost + length(roots)*log2(N);


end

