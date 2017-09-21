function [dNdx, dxdnat,J,detJ]= Element(xycoord, nat)
%xycoord= 4*2 matrix [x1,y1; x2,y2...] 
%nat= [zeta, nu]
%dxdnat= [dx/dzeta, dy/dzeta, dx/dnu, dy/nu ]
% dNdx= [dN1/dx  dN2/dx... ; dN1/dy , dN2,dy ...] 4*2
% zetas= [ -1; 1 ; 1; -1 ];
% nus= [-1 ; -1; 1 ; 1];
zetas = [1;1;-1;-1];
nus = [1;-1;-1;1];
dNidzeta= 0.25.*zetas.*(1+ nus.*nat(2)) ; 
dNidnu= 0.25.*nus.*(1+ zetas.*nat(1));

dxdnat= [0 0 0 0];
for i= 1:4 
    dxdnat(1) =dxdnat(1)+  0.25*zetas(i)*(1+ nus(i)*nat(2))*xycoord(i,1); 
    dxdnat(2) = dxdnat(2) + 0.25*zetas(i)*(1+ nus(i)*nat(2))*xycoord(i,2);
    dxdnat(3) = dxdnat(3) + 0.25*nus(i)*(1+ zetas(i)*nat(1))*xycoord(i,1); 
    dxdnat(4) = dxdnat(4) + 0.25*nus(i)*(1+ zetas(i)*nat(1))*xycoord(i,2);
end 

J = [dxdnat(1) , dxdnat(2); dxdnat(3), dxdnat(4)] ; 
detJ= det(J)  ;

for i = 1:4 
    dNdx(:,i)= J\[dNidzeta(i) ; dNidnu(i)];
end 
end 