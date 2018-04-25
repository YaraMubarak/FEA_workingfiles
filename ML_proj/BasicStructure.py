#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 16:41:18 2018

@author: ymubarak
"""

import numpy as np 
import meshpy.triangle as triangle
from sklearn import svm 
import matplotlib.pyplot as plt 
import feap #ur feap function 
import parser 

import sys 

# %% Pre-written Code 
def ellipse(x0,y0,a,b,angle, density = 20 ):
    # t = np.linspace(0, np.pi/2, num=int(N/4))
    # t = np.concatenate((t, t+np.pi/2,t+np.pi,t+3*np.pi/2), axis=0)
    t = np.linspace(0, 2*np.pi, num=density)
    x = a*np.cos(t)
    y = b*np.sin(t)
    R = np.array([[np.cos(angle), -np.sin(angle)], 
                  [np.sin(angle),  np.cos(angle)]])
    x,y = R.dot(np.vstack([x,y]))
    x,y = x+x0,y+y0
    ellipse = np.array([[x[i], y[i]] for i in range(density)])
    return ellipse


def round_trip_connect(start, end):
    return [(i, i+1) for i in range(start, end)] + [(end, start)]

def check_intersection_two_ellipses(ell1,ell2,kernel):
    """Find a boundary decision / a separation curve between the 2 ellipses"""
    X = np.concatenate((ell1,ell2),axis=0)
    y = np.concatenate((np.zeros(len(ell1)),np.ones(len(ell1))))
    if kernel=='rbf':
        clf = svm.SVC(kernel='rbf', C=1000) #'rbf' for the case of a ellipse inside another. 
        clf.fit(X, y)
    elif kernel == 'linear':
        clf = svm.SVC(kernel='linear', C=1000)
        clf.fit(X,y)
    result = clf.score(X,y)!=1 #True if intersecting (score = 1 only if the two clusters aren't crossing)
    return result

def checkIntersection(ell1,ell2):
    return check_intersection_two_ellipses(ell1,ell2,'linear') and check_intersection_two_ellipses(ell1,ell2,'rbf')

def refinement_func(tri_points, area,A=1 ):
    max_area=A
    return bool(area>max_area);

# %% Defining Structure 
    
class Lumen : 
    def __init__(self):
        self.loc = (np.random.normal(-0.8,0.2),0)
        self.d1 = np.random.normal(1.9,0.2)
        self.d2 = np.random.normal(2.3,0.2)
    def draw(self) : 
        hi= ellipse(self.loc[0], self.loc[1], self.d1, self.d2, 0)
        return [(x[0],x[1]) for x in list(hi)]
    
    def changeloc(self):
        self.loc = (np.random.normal(-0.8,0.2),0)
        
    def setloc(self,loc):
        self.loc = loc 
    


class Calcium : 
    def __init__(self) : 
        
        self.loc = (np.random.normal(2,0.3),np.random.normal(1.2,0.3))
        self.d1 = np.random.normal(0.5,0.2)
        self.d2 = np.random.normal(0.3,0.1)
        self.angle = np.random.uniform(low = 0 , high =2*np.pi )
        
        self.size = np.pi * self.d1 * self.d2 
    
    def draw(self) : 
        hi= ellipse(self.loc[0], self.loc[1], self.d1, self.d2, self.angle)
        return [(x[0],x[1]) for x in list(hi)]
    
    def changeloc(self): 
        self.loc = (np.random.normal(2,0.3),np.random.normal(1.2,0.3))
    
    def setloc(self,loc):
        self.loc = loc 

class Lipid: 
    def __init__(self):
        self.loc = (np.random.normal(1.9,0.3),np.random.normal(0,0.4))
        self.d1 = np.random.normal(0.7,0.2)
        self.d2 = np.random.normal(0.4,0.15)
        self.angle =  np.random.uniform(low = 0 , high =2*np.pi )
        
        self.size = np.pi * self.d1 * self.d2 
    def draw(self) : 
        hi =  ellipse(self.loc[0], self.loc[1], self.d1, self.d2, self.angle) 
        return [(x[0],x[1]) for x in list(hi)]
    
    def changeloc(self): 
        self.loc = (np.random.normal(1.9,0.3),np.random.normal(0,0.4))
    
    def setloc(self,loc):
        self.loc = loc 


class Artery: 
    
    def __init__(self) : 

        self.loc = (0,0)
        self.d1_inner = np.random.normal(3, 0.3)
        self.d2_inner = np.random.normal(2.8, 0.2)
        
        self.ratio = np.random.normal(1.07, 0.02)
        
        self.d1_outer = self.d1_inner*self.ratio
        self.d2_outer = self.d2_inner*self.ratio 
        
    def draw(self):
        out = ellipse(0,0, self.d1_inner, self.d2_inner, 0) 
        hi = np.vstack([out,ellipse(0,0, self.d1_outer, self.d2_outer, 0)  ])
        return [(x[0],x[1]) for x in list(hi)]
    def draw_inner(self):
        out = ellipse(0,0, self.d1_inner, self.d2_inner, 0) 
        return  [(x[0],x[1]) for x in list(out)]
    def draw_outer(self):
        out = ellipse(0,0, self.d1_outer, self.d2_outer, 0) 
        return  [(x[0],x[1]) for x in list(out)]
        

class Mesh: 
    def __init__(self, calcium = 1 , lipid = 1  ):
        self.cal_n = calcium 
        self.cal_l = lipid 
        self.a = Artery() 
        self.l = Lumen() 
        
        self.c = [Calcium() for i in range(calcium)]
        self.f = [Lipid() for i in range(lipid)]
        
        self.parts= [self.a, self.l] 
        self.parts.extend(self.c)
        self.parts.extend(self.f)
        
        while self.intersect() : 
            self.fix() 
            
        
        

            
    def intersect(self):
        ellipses = [np.array(x.draw()) for x in self.parts if x != self.a ]
        ellipses.append(self.a.draw_inner() )
        
        flag = False 
        for i in range(len(self.parts)): 
            for j in range(i,len(self.parts)):
                if i != j : 
                    flag = checkIntersection(ellipses[i],ellipses[j])
                if flag : 
#                    print(self.parts[i])
#                    print(self.parts[j])
                    return flag 
        
    def fix(self, ):
        
        #print('fixing')
        self.c = [Calcium() for i in range(self.cal_n)]
        self.f = [Lipid() for i in range(self.cal_n)]
        
        self.parts= [self.a, self.l] 
        self.parts.extend(self.c)
        self.parts.extend(self.f)
        
    
    def getpoints(self, calcium = 1 , lipid = 1 ):
        partnum = 1 
        
        points = []
        markers = [] 
        facets = [] 
        
        for part in self.parts: 
            start = len(points)
            points.extend(part.draw())
            end = len(points) - 1 
            markers.extend(len(part.draw())*[partnum])
            facets.extend(round_trip_connect(start, end))
            partnum = partnum + 1 
            
        self.points = points 
        self.markers = markers 
        self.facets = facets 
    
        
    def make_mesh(self, A=1 ):
        self.getpoints() 
        # build the triangles
        info = triangle.MeshInfo()
        info.set_points(self.points)
        info.set_holes([self.l.loc]) #the lumen is clear, it's a "hole"
        info.set_facets(self.facets, facet_markers=self.markers)

        info.regions.resize(len(self.parts))
        
        j = 1 
        
        wall_out_avg_x = (np.min(np.array(self.a.draw_inner())[:,0]) + np.min(np.array(self.a.draw_outer())[:,0]))/float(2)
        wall_in_avg_x = (np.min(np.array(self.a.draw_inner())[:,0]) + np.min(np.array(self.l.draw())[:,0]))/float(2)
        avgs = [wall_out_avg_x, wall_in_avg_x]
        for part in self.parts:
            if j > 2 : 
                info.regions[j - 1 ]= [part.loc[0], part.loc[1], j, A]
                j = j + 1
            else :
                info.regions[j - 1 ]= [avgs[j-1], 0, j, A]
                j = j + 1            
        self.mesh_ = triangle.build(info) 
        return self.mesh_
    
    def writefeapfile(self,filename ):
        file1 = open(filename+'.mesh','w')
        file1.write('coor\n')
        for i in list(range(1,len(self.mesh_.points)+1)):
            file1.write('%d 0 %1.4e %1.4e\n' % (i, self.mesh_.points[i-1][0], self.mesh_.points[i-1][1]) )
        file1.write('\n')
        file1.write('elem\n')
        for i in list(range(1,len(self.mesh_.elements)+1)):
            file1.write(str(i)+' '+str(0)+' '+str(int(self.mesh_.element_attributes[i-1]))+' '+str(self.mesh_.elements[i-1][0]+1)+' '+str(self.mesh_.elements[i-1][1]+1)+' '+str(self.mesh_.elements[i-1][2]+1)+'\n')
        file1.close()

        file2 = open(filename+'.pres','w')
        c = len(self.mesh_.elements)
        file2.write('elem,add\n')
        for i in range(len(np.arange(len(self.mesh_.points))[np.array(self.mesh_.point_markers) ==3])-1):
            file2.write('%d 9 0 %d %d\n' % (c+i+1,np.arange(len(self.mesh_.points))[np.array(self.mesh_.point_markers) ==3][i]+1,np.arange(len(self.mesh_.points))[np.array(self.mesh_.point_markers) ==3][i+1]+1))
        file2.close()

        file3 = open(filename+'.boun','w')
        file3.write('boun,add\n')
        for idx in np.arange(sum(self.mesh_.point_markers == 1) + 1 ):
            file3.write(str(idx+1)+' '+str(0)+' '+str(1)+' '+str(1)+'\n')
        file3.close()
        
    def appendfeature(self, featurmatrixtextfile):
        row = self.makefeaturearray()
        with open(featurmatrixtextfile, "a") as myfile:
            myfile.write(["%s" % item  for item in row])
            myfile.write("\n")
        #write feature to filename.txt with exisiting other features 
    def makefeaturearray(self):
        row = [] 
        
        for f in self.f: 
            row.append(f.size )
            row.append(f.loc[0])
            row.append(f.loc[1])
        
        for c in self.c: 
            row.append(c.size )
            row.append(c.loc[0])
            row.append(c.loc[1])
            
        return row
        #usually must return row of feature in numpy form 
    def appendlabel(self,labeltextfile):
        pass #same as features but for labels using readVM to get the VM stress 
    def runfeap(self,feapfilename,pressure):
        flag, outfile = feap(feapfilename,pressure)
        return flag,outfile 
    def readVM(self,outPutfile):
        p = parser.feapoutput(outPutfile) # imported object from parser.py 
        p.parse() 
        #### STILL NEED TO WRITE VM in parser ,  or you could write it here to get the Von misses from parser.stresslist 
        return 0 #should return labels 

class Structure : 
    def __init__(self,featurematrixfile,labelfile, feapinputfilename = '1'):
        self.f_i =  feapinputfilename
        self.f_o = [] 
        self.X_file =  featurematrixfile
        self.y_file = labelfile
    def run(self):
        m = Mesh()  
        m.make_mesh()
        m.writefeapfile(self.f_i)
        flag, outputfilename = m.runfeap(self.f_i )
        if flag : 
            m.readVM(outputfilename)
            m.appendfeature(self.X_file)
            m.appendlabel(self.y_file)
            print('done')
        else : 
            raise Exception('Cannot run feap ')
        

        
if __name__ == "__main__":
    s = Structure(sys.argv[0],sys.argv[1],feapinputfilename=sys.argv[2] )
    s.run() 

#plt.scatter(np.array(m.points)[:,0], np.array(m.points)[:,1])
 #, refinement_func=refinement_func, attributes=True)
    