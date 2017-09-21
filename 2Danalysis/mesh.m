function [xyz, cfixed,nelements,Bnodes]= mesh(n,m,L,h) 
% n is the number of nodes in x direction 
% m is the number of nodes in the y direction 
% L is length 
% h is height 
sizey= h/(m-1) ; 
sizex= L/(n-1);

%numbered as 
% 4o -- 5o -- 6o 
%    e1    e2
% 1o -- 2o -- 3o

%returns 
% xyz the geometric location of the nodes in xyz= [x1 y1; x2 y2 ; x3 y3...]
% cfixed is the connectivity matrix in order of elements
% nelements is the number of elements 
% Bnodes is boundary nodes with cells of arrays 
% of lower boundary nodes, right boundary nodes, 
% upper boundary nodes then left boundary nodes, respectively. 
xyz= zeros(n*m,2) ;
x = 0; 
for i = 1:n*m 
    elevation = floor((i-1)/n); 
    xyz(i,1)= (x)*sizex ;
    xyz(i,2)= elevation*sizey;
    if i>1 
        if  elevation ~= (xyz(i-1,2)/sizey)
            x= 0;
            xyz(i,1)= (x)*sizex ;
            x= x+1 ;
        else
            x= x+1 ;
        end 
    else 
        x= x+1; 
    end 
end


nelex= n-1 ; 
neley= m-1; 
nelements= nelex*neley;
connectivity= zeros(nelements, 4);
counterx = 0.5; 
countery= 0.5; 
nodenums= [ 1 2 0 0 ];
third= nodenums(1) + n  ;
fourth= nodenums(2) + n ; 
nodenums= [nodenums(1:2) , third ,fourth] ;
connectivity(1,:)= nodenums;
for i= 2: nelements
    firsttwo= nodenums(1:2) + 1; 
    if rem(firsttwo(1),n) == 0 
        firsttwo= firsttwo + 1 ; 
    end 
    third= firsttwo(1) + n ;
    fourth= firsttwo(2) + n ; 
    nodenums= [firsttwo , third fourth] ;
    connectivity(i,:)= nodenums;
end 


cfixed= [connectivity(:,3), connectivity(:,4), connectivity(:,2),connectivity(:,1) ];
lowerb = find(xyz(:,2)== 0);
rightb= find(xyz(:,1)== L );
upperb= find(xyz(:,2)== h );
leftb= find(xyz(:,1)== 0 );

Bnodes= [{lowerb}, {rightb},{upperb},{leftb}];

end 

