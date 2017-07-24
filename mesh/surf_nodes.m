function [surfacematrix]= surf_nodes(nodesonsurface,connectivity)

index= 1;
for row= 1:length(connectivity) 
    nodes=connectivity(row,:);
    if length(setdiff(nodes,nodesonsurface)) == 3
        surfacematrix(index,:) = setdiff(nodes,nodesonsurface);
        index= index + 1; 
    end 
end 
