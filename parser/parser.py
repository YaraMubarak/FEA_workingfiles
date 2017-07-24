# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 20:51:15 2017

@author: Ymubarak
"""
# fix stress object in list overlap 
# write exception 
import numpy as np 
import re 

class feapoutput() : 
    def __init__(self, path,nodenumber=[],elemnumber= []) : 
        self.path = path 
        self.filetext = open(path).readlines
        self.nodenumber = nodenumber
        self.elemnumber = elemnumber
        self.finaldisplacement = []
        self.finalstrain = []
        self.finalstress = []
        self.displacementlist = list() 
        self.stresslist = list() 
        self.solutiontimes = []
    def listidentifiers(self) : 
        iden= list() 
        iden.append("Number of Nodal Points") 
        iden.append("Number of Elements")
        iden.append( "N o d a l   D i s p l a c e m e n t s ")
        iden.append("Element Stresses")
        return iden 
    
    def parse(self) :
        readNextdisp = False 
        readNextstr= False
        idents = self.listidentifiers() 
        line_in = 0 
        str_current = stresses(0)
        startnew = True 
        for line in self.filetext() : 
            if idents[0] in line: 
                node=re.findall(r'\d+', line)
                nodes = [int(x) for x in node]
                self.nodenumber = nodes[0]
                
            if idents[1] in line: 
                elem=re.findall(r'\d+', line)
                elems = [int(x) for x in elem]
                self.elemnumber = elems[0]
            ## starting the displcament parser if reads identifier 
            if idents[2] in line :
                disp_current = displacement(self.nodenumber)
                disp_current.time = toNumpyRow(line)[0]
                readNextdisp = True 
                
            elif readNextdisp is True:
               readNextdisp = disp_current.read_line(line) 
               if disp_current.pointer == self.nodenumber + 3 :
                    self.finaldisplacement = disp_current
                    self.displacementlist.append(disp_current)
            
            ## read for the stresses
    
            if idents[3] in line and startnew is True :
                startnew = False 
                readNextstr = True 
                
            elif readNextstr is True:
               readNextstr = str_current.read_line(line) 

            if "Computing solution " in line :
                    readNextstr= False
                    non_formatted_nums = toNumpyRow(line,exception= True)
                    self.finalstress = str_current
                    self.stresslist.append(str_current)
                    str_current = stresses(self.elemnumber)
                    str_current.time = float(non_formatted_nums[0].replace(':',''))
                    startnew = True 
                    
            line_in = line_in + 1 
            
        self.finalstress = str_current
        self.stresslist.append(str_current)
        
        self.cleanup() 
    def cleanup(self) : 
        
        del self.stresslist[0]
        
        self.errors() 
        
        for x in self.stresslist : 
            x.strain_matrix = RemoveZeros(x.strain_matrix)
            x.stress_matrix = RemoveZeros(x.stress_matrix)
            
        
        self.finaldisplacement = self.displacementlist[len(self.stresslist) -1 ].matrix
        self.finalstress = self.stresslist[len(self.stresslist) -1 ].stress_matrix
        self.finalstrain = self.stresslist[len(self.stresslist) -1 ].strain_matrix
        
        if not not self.displacementlist: 
            self.solutiontimes = [x.time for x in self.displacementlist]
        elif not not self.stresslist : 
            self.solutiontimes = [x.time for x in self.stresslist]
        
        
        
    def errors(self):
        stresstimes = [x.time for x in self.stresslist]
        disptimes =  [x.time for x in self.displacementlist]
        check1 = stresstimes == disptimes 
        if check1 is not True : 
            print('The times for displacement and stress dont match up')
            print('displacement times : ' + str(disptimes)) 
            print('stress times : ' + str(stresstimes))
            
class displacement() : 
    def __init__(self, nodenumber): 
        self.time= []
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
        elif self.pointer < self.nodenumber + 3 :
            row = toNumpyRow(line)
    
            self.matrix = np.vstack([self.matrix, row])
        elif self.pointer >= self.nodenumber + 4 : 
            readNext= False 

        self.pointer = self.pointer  + 1 
        return readNext

class stresses():
    def __init__(self, elemnumber):
        self.identifier = "Element Stresses"
        self.time = []
        self.linepointer = 0 
        self.blockpointer = 0 
        self.nodepointer = 1 
        try :
            self.elemnumber = elemnumber
        except TypeError: 
            print('enter node number')
        self.stress_matrix = np.zeros([elemnumber,9])
        self.strain_matrix = np.zeros([elemnumber,9])
        self.stress_header = np.array(['11-stress','22-stress','33-stress','12-stress','23-stress',
                                       '31-stress','1-stress', '2-stress','3-stress'])
        self.strain_header = np.array(['11-strain','22-strain','33-strain','12-strain','23-strain',
                                       '31-strain','1-strain', '2-strain','3-strain'])

    def read_line(self,line):
        readNext = True 
        if self.blockpointer >=1 :
            row = toNumpyRow(line)
            if len(row)== 5 :
                self.nodepointer= row[0]
            elif len(row)== 6: 
                if self.linepointer == 0 : 
                    self.stress_matrix[int(self.nodepointer)-1 , 0:6]= row 
                    self.linepointer = 1
                elif self.linepointer == 1: 
                    self.strain_matrix[int(self.nodepointer)-1 , 0:6]= row 
                    self.linepointer = 2
                elif self.linepointer == 2 : 
                    self.stress_matrix[int(self.nodepointer)-1 , 6:9]= row[0:3]
                    self.strain_matrix[int(self.nodepointer)-1 , 6:9]= row[3:6] 
                    self.linepointer = 0 

            
            elif line == '\n':
                self.blockpointer= self.blockpointer + 1 
                if self.nodepointer < self.elemnumber: 
                    readNext = True 
                else : 
                    readNext = False 
            elif self.identifier in line : 
                self.blockpointer = self.blockpointer -1 
        else: 
            if line == '\n' and self.blockpointer == -1 :
                 self.blockpointer = self.blockpointer + 2
            elif line == '\n':
                self.blockpointer = -1

    
        return readNext 
    
        
def toNumpyRow(line, exception = False):
    numbstart= False 
    row = list() 
    for i in range(0,len(line)): 
       # print(line[i])
        #print(numbstart is True and not line[i].isdigit())
        if line[i].isdigit() and numbstart is False:
            numbstart= True 
            word = str(line[i])
        elif numbstart is True and line[i] is not ' ' and line[i] is not '\n':
            word= word + str(line[i])
        elif numbstart is True and not line[i].isdigit():
            numbstart = False 
            try :
                row.append(float(word))
            except ValueError :
                pass 
            if exception is True : 
                row.append(word)
    return np.array(row)

def RemoveZeros(numpy):
    tup = np.nonzero(numpy)
    cutat = tup[0][len(tup[0]) - 1]
    numpy = numpy[0:cutat, :]
    return numpy 