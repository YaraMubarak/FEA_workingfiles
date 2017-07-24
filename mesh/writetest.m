%Test writing 
A = [1,2,3; 1,2,3; 1,2,3];
fileID = fopen('writingtest.txt', 'wt');
fwrite(fileID,['hi', ' ',num2str(A(1,1)),' ',num2str(A(1,2)),' ',num2str(A(1,3))]);
fprintf(fileID,'\n');
fwrite(fileID, 'hi ');
fwrite(fileID, sprintf('hi %d 3 34 4',500));
fclose(fileID)

% fileID = fopen('writingtest.txt', 'a');
% 
% fclose(fileID)

