# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 20:51:15 2017

@author: Ymubarak
"""
import numpy as np 
import re 

class feapoutput() : 
    def __init__(self, path,nodenumber=[]) : 
        self.path = path 
        self.filetext = open(path).readlines
        self.nodenumber = nodenumber
        self.finaldisplacement = []
        self.displacementlist = list() 
        self.finalstress = []
        self.stresslist = list() 
    def listidentifiers(self) : 
        iden= list() 
        iden.append("Number of Nodal Points") 
        iden.append( "N o d a l   D i s p l a c e m e n t s ")
        iden.append("Element Stresses")
        return iden 
    def parse(self) :
        readNextdisp = False 
        readNextstr= False
        idents = self.listidentifiers() 
        line_in = 0 
        str_current = stresses(0)
        for line in self.filetext() : 
            if idents[0] in line: 
                node=re.findall(r'\d+', line)
                nodes = [int(x) for x in node]
                self.nodenumber = nodes[0]
                
            ## starting the displcament parser if reads identifier 
            if idents[1] in line :
                print(line_in) 
                disp_current = displacement(self.nodenumber)
                readNextdisp = True 
                
            elif readNextdisp is True:
               readNextdisp = disp_current.read_line(line) 
               if disp_current.pointer == self.nodenumber + 3 :
                    self.finaldisplacement = disp_current
                    self.displacementlist.append(disp_current)
            
            ## read for the stresses
    
            if idents[2] in line and str_current.blockpointer == 0 :
                print(line_in) 
                str_current = stresses(self.nodenumber)
                readNextstr = True 
                
            elif readNextstr is True:
               readNextstr = str_current.read_line(line) 
               print(line_in)
              # print(str_current.blockpointer)
               if str_current.nodepointer ==self.nodenumber :
                    self.finalstress = str_current
                    self.stresslist.append(str_current)
            line_in = line_in + 1 
            

class displacement() : 
    def __init__(self, nodenumber): 
        self.identifier =  "N o d a l   D i s p l a c e m e n t s "
        self.pointer= 0
        self.nodenumber = nodenumber 
        self.matrix = [] 
    def read_line(self,line):
        readNext = True 
        if self.pointer < 3 : 
            pass 
        elif self.pointer==3: 
            self.matrix= np.array(toNumpyRow(line))
            print('first line' + str(line))
        elif self.pointer < self.nodenumber + 3 :
            row = toNumpyRow(line)
    
            self.matrix = np.vstack([self.matrix, row])
        elif self.pointer >= self.nodenumber + 4 : 
            readNext= False 

        self.pointer = self.pointer  + 1 
        return readNext

class stresses():
    def __init__(self, nodenumber):
        self.identifier = "Element Stresses"
        self.linepointer = 0 
        self.blockpointer = 0 
        try :
            self.nodenumber = nodenumber
        except TypeError: 
            print('enter node number')
        self.stress_matrix = np.zeros([nodenumber,9])
        self.strain_matrix = np.zeros([nodenumber,9])
        self.stress_header = np.array(['11-stress','22-stress','33-stress','12-stress','23-stress',
                                       '31-stress','1-stress', '2-stress','3-stress'])
        self.strain_header = np.array(['11-strain','22-strain','33-strain','12-strain','23-strain',
                                       '31-strain','1-strain', '2-strain','3-strain'])
        self.nodepointer = 0 
    def read_line(self,line):
        readNext = True 
        if self.blockpointer >=1 :
            row = toNumpyRow(line)
            if len(row)== 5 :
                self.nodepointer= row[0]
            elif len(row)== 6: 
                if self.linepointer == 0 : 
                    self.stress_matrix[self.nodepointer-1 , 0:5]= row 
                elif self.linepointer == 1: 
                    self.strain_matrix[self.nodepointer-1 , 0:5]= row 
                elif self.linepointer == 2 : 
                    self.stress_matrix[self.nodepointer-1 , 5:8]= row[0:3]
                    self.strain_matrix[self.nodepointer-1 , 5:8]= row[3:6] 
                    self.linepointer = self.linepointer + 1 
            elif line == '\n':
                self.linepointer= 0 
                self.blockpointer= self.blockpointer + 1 
                if self.nodepointer < self.nodenumber: 
                    readNext = True 
                else : 
                    readNext = False 
            elif self.identifier in line : 
                self.blockpointer = self.blockpointer -1 
        else: 
            if line == '\n' and self.blockpointer == 'headerblock':
                 self.blockpointer = self.blockpointer + 1 
            elif line == '\n':
                self.blockpinter = 'headerblock'
        return readNext 
    
        
def toNumpyRow(line):
    numbstart= False 
    row = list() 
    for i in range(0,len(line)): 
        if line[i].isdigit() and numbstart is False:
            numbstart= True 
            word = str(line[i])
        elif numbstart is True and line[i] is not ' ' and line[i] is not '\n':
            word= word + str(line[i])
        elif numbstart is True and not line[i].isdigit():
            numbstart = False 
            row.append(float(word))
    return np.array(row) 
