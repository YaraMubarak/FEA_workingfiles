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
nn = length(xyz) ; %change 

ess_bound_mat = load('dsg-dirichlet.dat') ;

%% Assembling  

K = sparse(nn,nn);
M = sparse(nn,nn); 


% constant no matter what gauss point 
B = [-1 1 0; -1 0 1];


for el= 1: ne 
    
    nodes = connectivity(el,:) ; 
    X = xyz(nodes,:) ; 
    
    J = [X(2,1)-X(1,1) X(3,1)-X(1,1); X(2,2)-X(1,2) X(3,2)-X(1,2)];
    Jinv = inv(J);
    detJ = det(J);
    
    m = detJ *[2 1 1; 1 2 1; 1 1 2]/24; % mass matrix in local coordinates

    
    if detJ < 0 
        error('det <  0 : check element mapping order') 
    end 
    
    K(nodes, nodes) = K(nodes,nodes) + .5 * (B') * Jinv * (Jinv') * B * detJ;
    M(nodes, nodes) = M(nodes,nodes) + m ; 
end 


%% Solve for each time


trial = 3; 
endtime=3 ; 
tf = 0.0001 ; 
theta = 0 ;
ml = true  ; 

% set video and snapshot factors 
iters = length(0:tf:endtime) ; 
video_f = ceil(iters/100) ; 
snap = [video_f*3 , ceil(iters/2) , iters - video_f*3 ]; 


% dtest = [0];
% etest= [0];

v = VideoWriter(sprintf('vid%d.avi', trial)) ; 
open(v)


% Initializations 

idd = ess_bound_mat;
iddsing = idd ; 
% the rest 
idf =  setdiff(linspace(1,nn, nn), idd)';
idfsing = idf ;

% double up for new x which is d and e stacked 
idd = [idd; nn + idd] ; 
idf = [idf; nn + idf] ; 


%dirichlet boundary 
g = @(t) 0.05*sin(2*pi*3*t) ;
gd = @(t) -0.05*(2*pi*3)*cos(2*pi*3*t) ;
gdd = @(t) -0.05*(2*pi*3)^2 * sin(2*pi*3*t) ;

d_i =  zeros(nn, 1 ); %bc1
e_i = zeros(nn,1) ; %bc2 

i = 0 ; 
snapnum = 1 ; 
if ml 
    diags = sum(M,2) ; 
    minv = 1./diags; 
end

    
for t = tf:tf:endtime 
    F = zeros(nn,1);
    x_plus = zeros(2*nn,1) ; 
    
    
    % essential boundary nodes 
    F_i = zeros(nn,1) ; 
    F_plus = zeros(nn,1) ; 
    F_i(idfsing) = F(idfsing) - K(idfsing, iddsing)*ones(length(ess_bound_mat),1)*g(t-tf) - M(idfsing, iddsing)*ones(length(ess_bound_mat),1)*gdd(t-tf) ;
    F_plus(idfsing) = F(idfsing) - K(idfsing, iddsing)*ones(length(ess_bound_mat),1)*g(t) - M(idfsing, iddsing)*ones(length(ess_bound_mat),1)*gdd(t);
    Ftheta = theta*F_plus + (1-theta)*F_i; 
    
    % Solve for Ax = b 
    %make A 
    A = [M , -theta*tf*M ; theta*tf*K, M ];
    b = [M, (1-theta)*tf*M ; (theta-1)*tf*K , M ]*[d_i; e_i] + [zeros(nn,1); tf*Ftheta] ; 
    
    
    if not(ml) 
        x_plus(idf) = A(idf,idf)\b(idf) ; 
    else 
        if theta ~= 0 
            error('theta needs to be 0 ') 
        end 
        
        x_plus(idf) = [minv(idfsing);minv(idfsing)]'.*b(idf)  ; 
    end 
    
        
    x_plus(idd) = [ones(length(ess_bound_mat),1)*g(t) ; ones(length(ess_bound_mat),1)*gd(t) ]; 
        
    % replace d_i  and e_i for next time step 
    d_i = x_plus(1:nn) ; 
    e_i = x_plus(nn + 1 : 2*nn) ; 

%     dtest = [dtest, d_i(12)];
%     etest = [etest, e_i(12)] ; 
    
    trisurf(connectivity, xyz(:,1), xyz(:,2), d_i);
    xlim([-0.2 1])
    ylim([0 1])
    zlim([-0.1 0.1])
    
    
    if rem(i,video_f) == 0 
    frame = getframe(gcf);
    writeVideo(v,frame) ; 
    end 
    
    if sum(i  == snap) == 1 
        name = sprintf('snap%d_%d.jpg', [trial, snapnum]) ; 
        saveas(gcf,name) 
        snapnum = snapnum + 1 ; 
    end 
    i = i + 1 ; 
    
    

    
end 
close(v)

%plot(0:tf:endtime,dtest)
%plot(0:tf:endtime,etest)




