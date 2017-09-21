clear all 
%close all 
% 
xnodes=2;
ynodes=2; 
nodenum= xnodes*ynodes;
L= 9; 
h= 6; 
th= 1; 
sizey= h/(ynodes-1) ; 
sizex= L/(xnodes-1);
E=20000 ;
v= 0.3; 
q= 60 ; %F/m
[xyz, connectivity,nelements,BNodes]= mesh(xnodes,ynodes,L,h);

%% Make K 
%initializing
nat=(1/sqrt(3)).* [ -1 1;1 1; 1 -1;-1 -1];
w= [1 1 1 1] ; 
nint= length(w) ; 
dof= 2 ;
strain = [0 0 ; 0 0; 0 0];
[stress, D]= material(E,v,strain);
K = spalloc(2*nodenum,2*nodenum,8*nodenum);
F = zeros(2*nodenum,1);
c = zeros(2*nodenum,1);
for el= 1:nelements
    %make k 
    k= zeros(nint*dof, nint*dof);
    for i = 1:4
    nodes= connectivity(el,:);
    xycoord = xyz(nodes,:);
   [dNdx, dxdnat,J,detJ]= Element(xycoord, nat(i,:));
    if detJ < 0 
        error('Element Jacobian is not positive') 
    end 
    
    B = [dNdx(1,1),    0     , dNdx(1,2),    0    , dNdx(1,3) ,     0     , dNdx(1,4),    0     ;...
              0   , dNdx(2,1),      0   ,dNdx(2,2),    0      , dNdx(2,3) ,     0    , dNdx(2,4);...
         dNdx(1,1), dNdx(2,1) ,dNdx(1,2),dNdx(2,2), dNdx(1,3) , dNdx(2,3) , dNdx(1,4), dNdx(2,4)];
     
    dvol= th*w(i)* detJ; 
    k = k + (B'*D*B*th*dvol); 
    
    end
    %get K from small k  
    index= [2*(nodes(1))-1, 2*(nodes(1)),...
            2*(nodes(2))-1, 2*(nodes(2)),...
            2*(nodes(3))-1, 2*(nodes(3)),...
            2*(nodes(4))-1, 2*(nodes(4))];
    K(index,index)= K(index,index) + k ;
    
end 

%Fill in F for right boundary nodes 
j= 1 ;
for i = [BNodes{2}]'
    index= 2*i -1  ;
    if or(j== 1, j==length(BNodes{2})) 
        F(index)= F(index)+ (q*sizey)/2; 
    else 
        F(index)= F(index) + q*sizey; 
    end 
    j = j+1 ;
end 

%Fill in F for upper boundary nodes 
j= 1 ;
for i = [BNodes{3}]'
    index= 2*i  ;
    if or(j== 1, j==length(BNodes{3})) 
        F(index)= F(index)+ (q*sizey)/2; 
    else 
        F(index)= F(index) + q*sizey; 
    end 
    j = j+1 ;
end     

%% 
%Forced Displacement : 
% at lower boundary and left boundary 
%iddnodes= unique([BNodes{1}; BNodes{4}]);
idd= unique(sort([(2.*BNodes{4} -1); 2.*BNodes{1}]));
totalindices= 1:2*nodenum;
idf= setdiff(totalindices, idd);

% Perform the solve
Kff =  K(idf,idf); 
Kfd = K(idf, idd); % Complete
Kdf = K(idd,idf); % Complete
Kdd = K(idd,idd); % Complete
Ff  =  F(idf);% Complete

c(idf) = Kff\(Ff - Kfd*c(idd)); % Complete
F(idd) = Kdf*c(idf) + Kdd*c(idd); % Complete

%% plotting 
upperNodesx= 2*BNodes{3} -1;
upperNodesy= 2*BNodes{3};
rightNodesx= 2*BNodes{2} -1;
rightNodesy= 2*BNodes{2};
upperdispx= c(upperNodesx);
upperdispy= c(upperNodesy);
rightdispx= c(rightNodesx);
rightdispy=c(rightNodesy);
xcoordinates= 0:sizex:L;
ycoordinates= 0:sizey:h;
figure(1)
plot(xcoordinates,upperdispx)
hold on 
plot(xcoordinates, upperdispy)
legend('xdisplacement','ydisplacement')
title('Upper Boundary Node Displacement')
xlabel('Node ( 9cm/Node in length)') 
ylabel('Displacement [m]')


figure(2)
plot(ycoordinates,rightdispx)
hold on 
plot(ycoordinates, rightdispy)
legend('xdisplacement','ydisplacement')
title('Right Boundary Node Displacement')
xlabel('Node ( 9cm/Node in length)') 
ylabel('Displacement [m]')
hold on 

%% Make stress 
nat=(1/sqrt(3)).* [ -1 1;1 1; 1 -1;-1 -1];
w= [1 1 1 1] ; 
nint= length(w) ; 
dof= 2 ;
strain = [0 0 ; 0 0; 0 0];
[stress, D]= material(E,v,strain);
St= zeros(nelements,3);
for el= 1:nelements
    %make k 
    stlocal= zeros(3,1);
    for i = 1:4
    nodes= connectivity(el,:);
    xycoord = xyz(nodes,:);
   [dNdx, dxdnat,J,detJ]= Element(xycoord, nat(i,:));
    if detJ < 0 
        error('Element Jacobian is not positive') 
    end 
    
    B = [dNdx(1,1), 0 , dNdx(1,2) , 0 , dNdx(1,3) , 0 , dNdx(1,4),0;...
         0, dNdx(2,1), 0, dNdx(2,2) , 0 , dNdx(2,3) , 0 , dNdx(2,4);...
         dNdx(1,1), dNdx(2,1) , dNdx(1,2) , dNdx(2,2) , dNdx(1,3) , dNdx(2,3), dNdx(1,4),dNdx(2,4)];
    ind= [2*(nodes(1))-1, 2*(nodes(1)),...
            2*(nodes(2))-1, 2*(nodes(2)),...
            2*(nodes(3))-1, 2*(nodes(3)),...
            2*(nodes(4))-1, 2*(nodes(4))];
    clocal= c(ind); %removed sort 
    dvol= th*w(i)* detJ; 
    stlocal = stlocal + (D*B*clocal.*(th*dvol)); 
    
    end
    %get K from small k  
    index= [1,2,3];
    St(el,index)= St(el,index) + [stlocal]' ; %removed 4 
end 