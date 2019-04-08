#!/usr/bin/python
import os
import sys
sys.path.append("..")
sys.path.append(".")
from fileLoc import *

DAFListName = "DAF.list"
try:
    fileHandle = open(CURRENT_DIR + DAFListName, "r")
except IOError:
    print "Can't open " + DAFListName + "!"
    exit(1)
DAFList = fileHandle.readlines()
fileHandle.close()
for line in DAFList:
    print "------------Run DAF [" + line.replace("\n", "") + "]:"
    for i in range(2006, 2019):
        os.system(SCRIPT_DIR + "analyser.py " + line.replace("\n", "") + " " + str(i) + "-01-01 " + str(i) + "-12-31")



