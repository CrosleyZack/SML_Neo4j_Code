function [P PMIN uallnodes expandedtreenodes cost] = expandPathsAll2(PMIN, TREEMIN, markedpaths, treenodes, markedset,markedset2, W, isvis)
%----------------------------------------------------------------
% expand paths all ----------------------------------------------
%----------------------------------------------------------------
% Similar to expandPaths, but shows all short paths between marked
% vertices, and highlights the TREEMIN. Gives context.
% P: NxN merged all expanded paths graph (==candidate graph)
% uallnodes: nodes in P (expanded candidate graph)
% PMIN: NxN expanded TREEMIN
% expandedtreenodes: nodes in PMIN (expanded TREEMIN)

k = length(markedset2);
N = size(W,1);
P = sparse(N,N);

allnodes = markedset2;

src = []; dst = [];
[from to trash] = find(TREEMIN);
from = treenodes(from);
to = treenodes(to);

for i=1:length(to)
    reverse = false;
    if(isempty(find(markedset2 == from(i))))
        temp = from(i);
        from(i) = to(i);
        to(i) = temp;
        reverse = true;
    end
    
    paths = markedpaths{to(i)};
    
    ind = find([paths.id] == from(i)); 
    
    sp = paths(ind(1)).path; % first occurrence gives the shortest path
    
    allnodes = [allnodes sp];
    
    %sp
    for j=1:length(sp)-1
        if(reverse)
            src = [src; sp(j+1)];
            dst = [dst; sp(j)];
            P(sp(j+1),sp(j)) = W(sp(j+1),sp(j)); 
            PMIN(sp(j+1),sp(j)) = W(sp(j+1),sp(j));
            if(PMIN(sp(j),sp(j+1)) ~= 0) % loop
                if(length(find(markedset2==sp(j))) == 0)
                    PMIN(sp(j),sp(j+1)) = 0;
                else
                    PMIN(sp(j+1),sp(j)) = 0;
                end
            end
        else
            src = [src; sp(j)];
            dst = [dst; sp(j+1)];
            P(sp(j),sp(j+1)) = W(sp(j),sp(j+1)); 
            PMIN(sp(j),sp(j+1)) = W(sp(j),sp(j+1)); 
            if(PMIN(sp(j+1),sp(j)) ~= 0) % loop
                if(length(find(markedset2==sp(j+1))) == 0)
                    PMIN(sp(j+1),sp(j)) = 0;
                else
                    PMIN(sp(j),sp(j+1)) = 0;
                end
            end
            
        end
    end
   
end


% return expanded min-tree nodes
expandedtreenodes = markedset2';
expandedtreenodes = [expandedtreenodes; src; dst];
expandedtreenodes = unique(expandedtreenodes);

 if(isvis)
     %save('L2.mat','L2')
     [int a b] = intersect(expandedtreenodes,[markedset markedset2]);
	
     bg=visGraph(PMIN(expandedtreenodes,expandedtreenodes), expandedtreenodes, a, 1, 1);
     bg.view;
     
 end
% return expanded min-tree nodes
expandedtreenodes = markedset2';
expandedtreenodes = [expandedtreenodes; src; dst];
expandedtreenodes = unique(expandedtreenodes);

LENEXP = length(expandedtreenodes);

% selfnote: after expansion we might have loops,
% may need to run TREEMIN on PMIN again!
L2 = zeros(LENEXP+1, LENEXP+1);
L2(1:LENEXP, 1:LENEXP) = (PMIN(expandedtreenodes,expandedtreenodes));
L2(LENEXP+1, 1:LENEXP) = 100;

% log2N link to unmarked nodes only
[int a b] = intersect(expandedtreenodes,markedset2);
L2(LENEXP+1, a) = log2(N);


 if(isvis)
     %save('L2.mat','L2')
     [int a b] = intersect(expandedtreenodes,[markedset markedset2]);
	
     bg=visGraph(PMIN(expandedtreenodes,expandedtreenodes), expandedtreenodes, a, 1, 1);
     bg.view;
     
 end

if(sum(sum(L2))>0)
    D = 1./L2;
    D(D==Inf)=0;

    V=(1:LENEXP+1)';
    [i j w] = find(D);
    E = [i j w];
    GT= edmonds(V,E);
    TREEMAX=reconstruct(GT);

    unodes= unique([i;j]);
    T = zeros(LENEXP+1,LENEXP+1);
    T(1:max(unodes),1:max(unodes)) = full(TREEMAX);
    TREEMIN=L2.*logical(T);
    
     %if(~isvis)
     %   [int a b] = intersect(expandedtreenodes,markedset);
     %    bg=visGraph(full(TREEMIN), expandedtreenodes, a, 1, 1);
     %    bg.view;
     %    find(TREEMIN(end,:)>0)
     %end
    
    PMIN = sparse(N,N);
    PMIN(expandedtreenodes,expandedtreenodes) = TREEMIN(1:LENEXP, 1:LENEXP);
   
end


cost = full(sum(sum(PMIN)));

uallnodes = unique(allnodes);

end