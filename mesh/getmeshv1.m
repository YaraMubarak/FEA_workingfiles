clear all ; clc

%% Getting Semi-optimized mesh from stl valve geometry 
model= createpde(1);
gd = importGeometry(model,'valve_mesh_long3_cut.stl');
msh=generateMesh(model, 'GeometricOrder', 'linear');
%pdegplot(model);

%% getting loads in feap input form arrays: 
Nodes=msh.Nodes;
Nodes= Nodes'; 
Eles= msh.Elements; 
Eles= Eles'; 
mat= horzcat([1:1:length(Nodes)]', zeros(length(Nodes), 1)); 
Nodes= horzcat(mat,Nodes); 
mat= horzcat([1:1:length(Eles)]', zeros(length(Eles), 1)); 
mat= horzcat(mat, ones(length(Eles), 1));
Eles= horzcat(mat,Eles); 
clear mat 

%% Get nodes of top and bottom flat from justloads
ID= fopen('justloads.txt') ; 
C=textscan(ID,'%s');
txtcells= C{1} ; 

row= 0.5;  % row 1 is bottom flap , row 2 is upper flap 
j= 1;
for i= 1:length(txtcells) 
    txt= txtcells{i};
    if strmatch(txt, '<nodal_load') 
        row= round(row + 0.5); 
        j= 1; 
    end 
    if strmatch('id=', txt) 
        sizeofnumber= length(txt) - 14 ; 
        node= str2num(txt(5:(5+sizeofnumber -1)));
        mat(row, j)= node;
        j = j+1 ;
    end 
end 

upper = mat(2,:);
lower = mat(1,:);

%remove zeros 
boolean1= upper ~= 0 ; 
boolean2= lower ~= 0 ; 

upper = upper(boolean1) ; 
lower= lower(boolean2); 

clear mat 

%% plot lower and upper flaps to make sure 

uxyz = Nodes(upper, 3:5); 
lxyz= Nodes(lower, 3:5) ; 

%% making the load file 

loadinpt1= horzcat([1:length(uxyz)]', uxyz);
loadinpt1= horzcat(loadinpt1, -1.*(ones(length(uxyz), 1))); 

loadinpt2= horzcat([1:length(lxyz)]', lxyz);
loadinpt2= horzcat(loadinpt2, -1.*(ones(length(lxyz), 1))); 

%% finding the normals to nodes 

%pdeplot3D(model)
[p,e,t] = model.Mesh.meshToPet();
A = e.getElementFaces(3);
A= A';
norms=getnormal(A, Nodes(:,3:5));

%plot one face and make sure 
% trinodes= A(1,:) ;
% trixyz= Nodes(trinodes, 3:5) ;
% norm_1= norms(1,:)' ;
% line_1 = trixyz(1,:) - trixyz(2,:) ; 
% 
% facenodes= vertcat(unique(A(:,1)),unique(A(:,2)), unique(A(:,3)));
% Axyz= Nodes(facenodes, 3:5) ;
% length(find(round(norms(:,2),2)))