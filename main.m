function main(edgefile, markedset,markedset2)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%% write the marked set file %%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
dlmwrite('marked-nodes.txt',markedset','delimiter',' ','precision','%6.0f');

% build the undirected unweighted adjacency matrix A
[src,dst , ~] = textread(edgefile);
N = max([src; dst]);
log2(N)

A = sparse(src, dst, ones(length(src),1), N, N);
A = A+A';
A(A>0) = 1;

% visualize the graph
if(N<=100)
bg = visGraph(A, [], markedset,0,0);
bg.view;
end

fprintf('There are %d edges in the graph...\n', full(sum(sum(A))/2));
deg = sum(A,2);
logdeg = log2(deg+1);

W = (A'*spdiags(logdeg, 0, N, N))';

clear A;

tStart = tic;
[markedpaths] = ShortPaths( W, logdeg, markedset );
tElapsed = toc(tStart)
disp('markedpaths computed!')

tStart = tic;
[SP, TREEMIN, trash, roots] = findMST(markedpaths, markedset); % TREEMIN is kxk where k = |markedset|
tMSTelapsed = toc(tStart)

[trash, PMIN, trash, trash, cost] = expandPathsAll(SP, TREEMIN, markedpaths, markedset, markedset, W, 1);

PMIN
fprintf('Cost-alg from MST TREE is %f \n', cost+length(roots)*log2(N));
cost = findTreeCost( PMIN, markedset, markedset(roots), deg );
fprintf('Cost-act from MST TREE is %f \n', cost);

[src dst trash] = find(PMIN);
tree = [src dst];
dlmwrite('tree-arb.txt',tree,'delimiter',' ','precision','%6.0f');
pause
bioc
tStart = tic;
[markedpaths2] = ShortPaths2( W, logdeg, markedset2, markedpaths );
tElapsed = toc(tStart)
disp('markedpaths 2 computed!')

tStart = tic;
[SP, TREEMIN, trash, roots] = findMST2(markedpaths2 ,markedset, markedset2, SP, TREEMIN); % TREEMIN is kxk where k = |markedset|
tMSTelapsed = toc(tStart)

[trash, PMIN, trash, trash, cost] = expandPathsAll(SP, TREEMIN, markedpaths2, [markedset markedset2], [markedset markedset2], W, 1);

pause