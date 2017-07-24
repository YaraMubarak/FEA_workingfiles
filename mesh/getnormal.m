function [normaltofaces] = getnormal(nodesoffaces, connectivity)
for i = 1: length(nodesoffaces) 
    for j = 1:3 
    point(j,:) = connectivity(nodesoffaces(i,j), :);
    end 
    v1 = point(1,:) - point(2,:);
    v2 = point(1,:) - point(3,:);
    normal = cross(v1,v2) ; 
    unitnormal = normal./(norm(normal));
    normaltofaces(i,:) = unitnormal; 
end 
