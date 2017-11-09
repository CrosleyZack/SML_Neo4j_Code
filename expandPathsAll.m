function [P PMIN uallnodes expandedtreenodes cost] = expandPathsAll(SP, TREEMIN, markedpaths, treenodes, markedset, W, isvis)
%----------------------------------------------------------------
% expand paths all ----------------------------------------------
%----------------------------------------------------------------
% Similar to expandPaths, but shows all short paths between marked
% vertices, and highlights the TREEMIN. Gives context.
% P: NxN merged all expanded paths graph (==candidate graph)
% uallnodes: nodes in P (expanded candidate graph)
% PMIN: NxN expanded TREEMIN
% expandedtreenodes: nodes in PMIN (expanded TREEMIN)



k = length(markedset);
[from to trash] = find(SP(1:k,1:k));
from = markedset(from);
to = markedset(to);

N = size(W,1);
P = sparse(N,N);

allnodes = markedset;
for i=1:length(to)
    paths = markedpaths{to(i)};
    if(isempty(paths))
        continue;
    end
    ind = find([paths.id] == from(i)); 
    if(isempty(ind))
        continue;
    end
    sp = paths(ind(1)).path; % first occurrence gives the shortest path
    %sp
    allnodes = [allnodes sp];
    for j=1:length(sp)-1
        P(sp(j),sp(j+1)) = W(sp(j),sp(j+1));  
    end
    
    for k=2:min(4,length(ind)) %   --lets get only top 3 shortest paths to keep the candidate graph small for now
        sp = paths(ind(k)).path; 
        %sp
        allnodes = [allnodes sp];
        for j=1:length(sp)-1
            P(sp(j),sp(j+1)) = W(sp(j),sp(j+1));        
        end
    end
    
end

% visualize before expansion
if(isvis)
[int a b] = intersect(treenodes,markedset);
bg=visGraph(full(TREEMIN), treenodes, a, 1, 1);
bg.view;
end
%length(unique(allnodes))


src = []; dst = [];
[from to trash] = find(TREEMIN);
from = treenodes(from);
to = treenodes(to);

PMIN = sparse(N,N);
for i=1:length(to)
    reverse = false;
    if(isempty(find(markedset == from(i))))
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
                if(length(find(markedset==sp(j))) == 0)
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
                if(length(find(markedset==sp(j+1))) == 0)
                    PMIN(sp(j+1),sp(j)) = 0;
                else
                    PMIN(sp(j),sp(j+1)) = 0;
                end
            end
            
        end
    end
   
end


% return expanded min-tree nodes
expandedtreenodes = markedset';
expandedtreenodes = [expandedtreenodes; src; dst];
expandedtreenodes = unique(expandedtreenodes);

LENEXP = length(expandedtreenodes);


addpath('edmonds')
% selfnote: after expansion we might have loops,
% may need to run TREEMIN on PMIN again!
L2 = zeros(LENEXP+1, LENEXP+1);
L2(1:LENEXP, 1:LENEXP) = (PMIN(expandedtreenodes,expandedtreenodes));
L2(LENEXP+1, 1:LENEXP) = 100;

% log2N link to unmarked nodes only
[int a b] = intersect(expandedtreenodes,markedset);
L2(LENEXP+1, a) = log2(N);


 if(isvis)
     %save('L2.mat','L2')
     [int a b] = intersect(expandedtreenodes,markedset);
	
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


if(isvis)
    cgsize = length(uallnodes)
    if(cgsize<100) % visualize
        [int a b] = intersect(uallnodes,markedset);
        bg = visGraph(P(uallnodes,uallnodes), uallnodes, a,1,1);
        [src dst w] = find(PMIN);
        % mark the edges
        for i=1:length(src)
            %['Node',' ',num2str(src(ind(i)))]
            %['Node',' ',num2str(dst(ind(i)))]
            h=getedgesbynodeid(bg,num2str(src(i)),num2str(dst(i)));
            set(h,'LineColor',[0 0 1]);
            set(h,'LineWidth',2);
        end
        bg.view;
    else
        [int a b] = intersect(expandedtreenodes,markedset);
        bg = visGraph(PMIN(expandedtreenodes,expandedtreenodes), expandedtreenodes, a,1,1);
        bg.view;
    end
end
end