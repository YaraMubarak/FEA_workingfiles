#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 21:01:16 2018

@author: bakhaty
"""
import subprocess
from threading import Timer
import sys 

TIMEOUT = 5 # seconds before killing process 
datapoints = 100 

class FEA_program: 
    def __init__(self):
        self.timeout = sys.argv[0]
        self.X = [] 
        self.y = []
        self.Meshes = []
        
    

if __name__=="__main__":
    it =0 
    successits = 0 
    while successits < datapoints:
        success = False
    
        try:
            ping = subprocess.Popen(['python BasicStructure.py featurematrix.txt labels.txt ' + str(successits) ], 
                                stdout=subprocess.PIPE, shell=True)
            my_timer = Timer(TIMEOUT, lambda process: process.kill(), [ping])
            my_timer.start()
            stdout, stderr = ping.communicate()
            print(stdout.decode())
            if len(stdout.decode())>0:
                success = True
                successits = successits + 1 
        except:
            my_timer.cancel()
        
        if success:
            print('success ' + str(it))
        else:
            print('failure ' + str(it))
            
        it = it  + 1 
