%get mesh version 2 
clear all; clc 

%% getting mesh from file 
model= createpde(1);
gd = importGeometry(model,'valve_mesh_long3_cut.stl');
msh=generateMesh(model, 'GeometricOrder', 'linear');
Nodes=msh.Nodes';
Eles= msh.Elements'; 

%% Rotate to Align with z axis instead of y 
th= -pi/2; 
Rot= [1,0,0; 0 ,cos(th), sin(th); 0, -sin(th), cos(th)];


%rotate to make face 3 at X axis (angle at 30) with mirroring
alpha = -30- 180; 
Rot2= [cosd(alpha), sind(alpha), 0;  -sind(alpha), cosd(alpha), 0; 0,0,1]; 

Nodes= Nodes*Rot';
Nodes = Nodes*Rot2';
%% finding the normals to nodes 
[p,e,t] = model.Mesh.meshToPet();
for i= 1:7 
    A = e.getElementFaces(i);
    A= A';
    norms{i}=getnormal(A, Nodes);
end 

%% for faces 3 and 4 get angles with which to rotate around z 
for face= 3:4 
    norm_mat = norms{face};
    if not (isempty(find(round(norm_mat(:,3),2))))
        disp('not orthogonal to z ; use a different Rotation matrix')
    end 
    angles{face-2} = radtodeg(acos(norm_mat(:,1))); %Notice they are the same angles ... due to SOLIDWORKS cutting 
end 



%% Get nodes of top and bottom flat from justloads.txt 
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

uppersurf= surf_nodes(upper,Eles) ; 
lowersurf= surf_nodes(lower,Eles); 

%% making the .mesh file 
mat= horzcat([1:1:length(Nodes)]', zeros(length(Nodes), 1)); 
NF= horzcat(mat,Nodes); 
mat= horzcat([1:1:length(Eles)]', zeros(length(Eles), 1)); 
mat= horzcat(mat, ones(length(Eles), 1));
EF= horzcat(mat,Eles); 
clear mat 

fileID = fopen('inp_v2.mesh', 'wt');
fprintf(fileID,'coor');
fprintf(fileID,'\n');
for i = 1:length(NF)
    for j = 1:length(NF(1,:))
        fwrite(fileID, [num2str(NF(i,j)),' ']) ;
    end 
    fprintf(fileID,'\n');
end 

fprintf(fileID,'\n');
fprintf(fileID,'elem');
fprintf(fileID,'\n');
for i = 1:length(EF)
    for j = 1:length(EF(1,:))
        fwrite(fileID, [num2str(EF(i,j)),' ']) ;
    end 
    fprintf(fileID,'\n');
end 

fclose(fileID);

%% making the load file 

fileID = fopen('inp_v2.load', 'wt');
fprintf(fileID,'load prop 1');
fprintf(fileID,'\n');
fprintf(fileID,'\n');

for i= 1:length(uppersurf) 
    fprintf(fileID,'csurf');
    fprintf(fileID,'\n');
    fprintf(fileID,'normal');
    fprintf(fileID,'\n');
    fprintf(fileID,'surface');
    fprintf(fileID,'\n');
    for j = 1:3 
        XYZ= Nodes(uppersurf(i,j),:);
        fprintf(fileID,sprintf('%d %d %d %d -1', [j XYZ]));
        fprintf(fileID,'\n');
    end 
    fprintf(fileID,'\n');
end 

fprintf(fileID,'\n');
fprintf(fileID,'load prop 2');
fprintf(fileID,'\n');
fprintf(fileID,'\n');

for i= 1:length(uppersurf) 
    fprintf(fileID,'csurf');
    fprintf(fileID,'\n');
    fprintf(fileID,'normal');
    fprintf(fileID,'\n');
    fprintf(fileID,'surface');
    fprintf(fileID,'\n');
    for j = 1:3 
        XYZ= Nodes(lowersurf(i,j),:);
        fprintf(fileID,sprintf('%d %d %d %d -1', [j XYZ]));
        fprintf(fileID,'\n');
    end
    fprintf(fileID,'\n');
end

fprintf(fileID,'\n');
fprintf(fileID,'load end');

fclose(fileID);

%% making the bound arrays for top and bottom (with no rotation ) faces 5 and 7
index= 1 ;
for i = [5,7]
    A = e.getElementFaces(i);
    A= A';
    n_uniq= unique(A) ; 
    mat = horzcat(n_uniq, zeros(length(n_uniq),3), ones(length(n_uniq),1));
    array{index}= mat;
    clear mat 
    index= index +1 ;
end 

fileID = fopen('inp_v2.boun', 'wt');
fprintf(fileID,'boun');
fprintf(fileID,'\n');
for i = 1:length(array{1})
    for j = 1:length(array{1}(1,:))
        fwrite(fileID, [num2str(array{1}(i,j)),' ']) ;
    end 
    fprintf(fileID,'\n');
end 

fprintf(fileID,'\n');
fprintf(fileID,'boun,add');
fprintf(fileID,'\n');
for i = 1:length(array{2})
    for j = 1:length(array{2}(1,:))
        fwrite(fileID, [num2str(array{2}(i,j)),' ']) ;
    end 
    fprintf(fileID,'\n');
end 

fclose(fileID);

%% adding the rotation for faces 3 and 4 to the .boun  file 
%since they all have th same angle 
index= 1 ;
for i = [3,4]
    A = e.getElementFaces(i);
    A= A';
    n_uniq= unique(A) ; 
    mat = horzcat(n_uniq, zeros(length(n_uniq),1), angles{i-2}(1)*ones(length(n_uniq),1));
    array{index}= mat;
    clear mat 
    index= index +1 ;
end 

mat = vertcat(array{1},array{2});

fileID = fopen('inp_v2.boun', 'a');
fprintf(fileID,'\n');
fwrite(fileID, 'boun, add ');
fprintf(fileID,'\n');
for i = 1:length(mat)
    fwrite(fileID, sprintf('%d 0 1 0 0', mat(i)));
    fprintf(fileID,'\n');
end 

fprintf(fileID,'\n');

for i = 1:length(mat)
    fwrite(fileID, 'angle ');
    for j = 1:length(mat(1,:))
        fwrite(fileID, [num2str(mat(i,j)),' ']) ;
    end 
    fprintf(fileID,'\n');
end 
clear mat 
%% write the .spring file for the back face (6) 
in_start = length(EF) +1 ; 
A = e.getElementFaces(6);
A= A';
uniq_nodes= unique(A) ; 
mat = horzcat([in_start: (in_start + length(uniq_nodes) -1)]',...
    zeros(length(uniq_nodes),1),2*ones(length(uniq_nodes),1) ,uniq_nodes);

fileID = fopen('inp_v2.spring', 'wt');
fprintf(fileID,'elem');
fprintf(fileID,'\n');
for i = 1:length(mat)
    for j = 1:length(mat(1,:))
        fwrite(fileID, [num2str(mat(i,j)),' ']) ;
    end 
    fprintf(fileID,'\n');
end 
fclose(fileID) ;
spring_in= mat(length(mat),1);

%% make .pres file 

% unify normal

ns= getnormal(lowersurf, Nodes) ;
for i = 1:length(lowersurf) 
    if ns(i,3) > 0 
        new = lowersurf(i,:) ;
        new(2) = lowersurf(i,3) ;
        new(3) = lowersurf(i,2) ; 
        lowersurf(i,:) = new ;
    end 
end 
ns= getnormal(lowersurf,Nodes);
check1 = length(ns(ns(:,3)>0))

ns= getnormal(uppersurf, Nodes) ;
for i = 1:length(uppersurf) 
    if ns(i,3) < 0 
        new = uppersurf(i,:) ;
        new(2) = uppersurf(i,3) ;
        new(3) = uppersurf(i,2) ; 
        uppersurf(i,:) = new ;
    end 
end 

ns= getnormal(uppersurf,Nodes);
check2 = length(ns(ns(:,3)<0))

fileID = fopen('inp_v2.pres', 'wt');
fprintf(fileID,'elem');
fprintf(fileID,'\n');
face_in= spring_in +1; 
for i = 1:length(lowersurf) 
    str= sprintf('%d 0 5 %d %d %d', [face_in lowersurf(i,:)]);
    face_in = face_in +1 ; 
    fprintf(fileID, str);
    fprintf(fileID,'\n');
end 

fprintf(fileID,'\n');
fprintf(fileID,'elem');
fprintf(fileID,'\n');
for i = 1:length(uppersurf) 
    str= sprintf('%d 0 6 %d %d %d', [face_in uppersurf(i,:)]);
    face_in = face_in +1 ; 
    fprintf(fileID, str);
    fprintf(fileID,'\n');
end 

fclose(fileID) ;
