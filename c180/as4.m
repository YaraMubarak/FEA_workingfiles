 % Author: Yara Mubarak 
% Class : ME C180 
% Date : 11/3/2018
% Version 1
% Assignment 3 
clear all , close all , clc 
%% Loading Data 

xyz = load('dsg-coordinates.dat');
connectivity = load('dsg-connectivity.dat');
ne = length(connectivity) ; 
nn = length(xyz) ; 

ess_bound_mat = load('dsg-dirichlet.dat') ;

%% Assembling  

K = sparse(nn,nn);
M = sparse(nn,nn); 


% constant no matter what gauss point 
B = [-1 1 0; -1 0 1];
gpnts = [0.5, 0.5 , 0 ; 0.5 , 0 , 0.5];
B_mass = zeros(3,3);
for i = 1 : 3 
    r = gpnts(1,i);
    s = gpnts(2,i) ; 
    
    Q  = [r r ; s s ; 1-r-s , 1-r - s ];
    B_mass = 0.5*Q*Q' + B_mass ; 
end 

% B_mass_ij = integral(N_i * N-j) in natural coordinates using 3 point gauss



for el= 1: ne 
    
    nodes = connectivity(el,:) ; 
    X = xyz(nodes,:) ; 
    
    J = [X(2,1)-X(1,1) X(3,1)-X(1,1); X(2,2)-X(1,2) X(3,2)-X(1,2)];
    Jinv = inv(J);
    detJ = det(J);
    
    if detJ < 0 
        error('det <  0 : check element mapping order') 
    end 
    
    K(nodes, nodes) = K(nodes,nodes) + .5 * (B') * Jinv * (Jinv') * B * detJ;
    M(nodes, nodes) = M(nodes,nodes) + B_mass*detJ ; 
    
end 


%% Solve for each time

idd = ess_bound_mat;
% the rest 
idf =  setdiff(linspace(1,nn, nn), idd)';

% double up for new x which is d and e stacked 
idd = [idd; nn + idd] ; 
idf = [idf; nn + idf] ; 


%dirichlet boundary 
g = @(t) 0.05*sin(2*pi*3*t) ;
gd = @(t) -0.05*(2*pi*3)*cos(2*pi*3*t) ;
gdd = @(t) -0.05*(2*pi*3)^2 * sin(2*pi*3*t) ;

d_i =  zeros(nn, 1 ); %bc1
e_i = zeros(nn,1) ; %bc2 

endtime =3 ; 
tf = 0.001 ; 
theta = 0.5 ;

dtest = [0];
etest= [0];
for t = tf:tf:endtime 
    F = zeros(nn,1);
    x_plus = zeros(2*nn,1) ; 
    
    
    % essential boundary nodes 
    F_i = F - K*ones(nn,1)*g(t-tf) - M*ones(nn,1)*gdd(t-tf) ;
    F_plus = F - K*ones(nn,1)*g(t-tf) - M*ones(nn,1)*gdd(t-tf);
    Ftheta = theta*F_plus + (1-theta)*F_i; 
    
    % Solve for Ax = b 
    %make A 
    A = [M , -theta*tf*M ; theta*tf*K, M ];
    b = [M, (1-theta)*tf*M ; (theta-1)*tf*K , M ]*[d_i; e_i] + [zeros(nn,1); tf*Ftheta] ; 
    
    x_plus(idf) = A(idf,idf)\b(idf) ; 
    x_plus(idd) = [ones(length(ess_bound_mat),1)*g(t) ; ones(length(ess_bound_mat),1)*gd(t) ]; 
        
    % replace d_i  and e_i for next time step 
    d_i = x_plus(1:nn) ; 
    e_i = x_plus(nn + 1 : 2*nn) ; 

    dtest = [dtest, d_i(10)];
    etest = [etest, e_i(10)] ; 
    
    trisurf(connectivity, xyz(:,1), xyz(:,2), d_i)

end 

plot(0:tf:endtime,dtest)
plot(0:tf:endtime,etest)




