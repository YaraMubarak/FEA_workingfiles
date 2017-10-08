% get flap faces 
model= createpde(1);
gd = importGeometry(model,'valve_mesh_long3_cut.stl');
msh=generateMesh(model, 'GeometricOrder', 'linear');
[p,e,t] = model.Mesh.meshToPet();

flap = e.getElementFaces(1);
flap = unique(flap) ; 

 fileID = fopen('flapnodes', 'wt');
 for i= 1:length(flap) 
     fprintf(fileID,string(flap(i)));
     fprintf(fileID,'\n');
 end 
 fclose(fileID) 