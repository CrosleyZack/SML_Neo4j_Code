function A = PruneGraph(A, markedset)

count=0;

N = size(A,1); 

marked = sparse(N,1);
marked(markedset) = 1;


deg = sum(A,2);
ind = find(deg==1 & marked==0);
len=length(ind);

while(len>0)
   
   count=count+len; 
   A(ind,:)=0; 
   A(:,ind)=0; 
   
   deg = sum(A,2);
   ind = find(deg==1 & marked==0);
   len=length(ind);
end

fprintf('%d vertices pruned...\n',count);

end