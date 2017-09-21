function [stress, D]= material(E,v,strain)
% v is poisson's number and E is elasticity 
%special case of plane stress 
D= (E/(1-v^2)).*[ 1, v , 0 ; ... 
                   v ,1, 0 ; ... 
                   0, 0 , 0.5*(1-v)];
              
strain0 = [0,0,0];
stress= D*(strain(:,1)- strain0);
end 


