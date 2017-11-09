function bg = visGraph(A, ids, markedset, arrows, weights)

% ids: ids of nodes in A, if empty increasing by 1 by default

if(isempty(ids))
    bg=biograph(A);
else
    lbl = cell(length(ids),1);
    for i=1:length(ids)
        lbl{i}=num2str(ids(i));
    end
    bg=biograph(A,lbl);
end


    
if(~arrows)
    bg.ShowArrows='off';
end
if(~weights)
    bg.ShowWeights='off';
else
    bg.ShowWeights='on';
end
bg.LayoutType='equilibrium';
%bg.view;

% change the color of the marked nodes
for i=1:length(markedset)
    bg.nodes(markedset(i)).color=[1,.5,0];
end


end