# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 19:21:44 2017

@author: Ymubarak
"""
import numpy as np 
import re 

class outputfile():
    def __init__(self,path):
        self.path = path
        self.file = open(path)
        self.lines = self.file.readlines() 
    def getnodenumber(self) : 
        identifier= "Number of Nodal Points"
        for i in range(0,len(self.lines)): 
            if identifier in self.lines[i] :
                index= i 
                break 
        node=re.findall(r'\d+''.', self.lines[index])
        nodes = [int(x) for x in node]
        return nodes[0]

class displacements():
    def __init__(self,outputfile):
        self.feapfile = outputfile 
        self.str_identifier = "n o d a l   d i s p l a c e m e n t s"
        self.header_to_start = 4 
    def parser(self):
        
        
def ToNumpyRow(text, index):
    test = text[index]
    numbstart= False 
    row = list() 
    for i in range(0,len(test)): 
        if test[i].isdigit() and numbstart is False:
            numbstart= True 
            word = str(test[i])
        elif numbstart is True and test[i] is not ' ' and test[i] is not '\n':
            word= word + str(test[i])
        elif numbstart is True and not test[i].isdigit():
            numbstart = False 
            row.append(float(word))
    return np.array(row)

def intomatrix(text, start, end):

    matrix = text[start:end]
    numpy = ToNumpyRow(matrix,0 )
    for row_in in range(1,len(matrix)):
        numpy= np.vstack([numpy, ToNumpyRow(matrix, row_in)])
    return numpy 
        
        