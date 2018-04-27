#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 21:01:16 2018

@author: bakhaty
"""
import subprocess
from threading import Timer
from multiprocessing import Pool
import sys 

TIMEOUT = 5 # seconds before killing process 
NUMPROC = 2
DATAPOINTS = 2 # THIS multiplies numproc

class FEA_program: 
    def __init__(self):
        self.timeout = sys.argv[0]
        self.X = [] 
        self.y = []
        self.Meshes = []
        

def run_process(pid):   
    
    cmd = 'python BasicStructure.py featurematrix%d.txt labels%d.txt test%d' \
          % (pid, pid, pid)  

    it =0 
    successits = 0 
    while successits < DATAPOINTS:
        success = False
    
        try:
            ping = subprocess.Popen([cmd + str(successits) ], 
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
            print(pid, ': success ' + str(it))
        else:
            print(pid, ': failure ' + str(it))
            
        it = it  + 1 


if __name__=="__main__":

    # create pool
    pool = Pool(NUMPROC)
    pool.map(run_process, list(range(NUMPROC)))
    pool.join()
    pool.close()



