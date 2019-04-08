#!/usr/bin/python

import os
import glob
import re
import sys
sys.path.append("..") 
from fileLoc import *


argc = len(sys.argv)
if argc != 2:
    print "Usage: genDAF.py DAFName"
    exit(1)
dafName = sys.argv[1]
dafDir = "./" + dafName + "/"
dafFile = "DAF_" + dafName
print "Generating new DAF: " + dafName
if not os.path.exists(dafDir):
    os.mkdir(dafDir)
else:
    print "The DAF has already been created: " + dafName
    exit(1)

with open(TEMPLET_DIR + "templet.h", "r") as templetHead, open(TEMPLET_DIR + "templet.daf", "r") as templetBody, open(dafDir + dafFile + ".h", "w") as dafHead, open(dafDir + dafFile + ".cpp", "w") as dafBody:
    content = templetHead.read()
    content = content.replace("__xxxxxx__", dafName)
    dafHead.write(content)
    content = templetBody.read()
    content = content.replace("__xxxxxx__", dafName)
    dafBody.write(content)

print "Done!"



'''
listglob = []
listglob = glob.glob(r"DAF_*.h")
print "Found: ",
print listglob
fileCount = len(listglob)
try:
    fileHandle = open("./register.g", "w")
except IOError:
    print "Can't open register.g"
    exit(1)

context = \
"/*********************************************************************\n\
 * register.cpp: auto generated, don't modify this file directly     *\n\
 *                                            2018 Hui               *\n\
 *********************************************************************/\n\n\
#include \"buyer.h\"\n\
#include \"DAF.h\"\n"

for i in range(0, fileCount):
    context = context + "#include \"" + listglob[i] + "\"\n"

context1 = \
"\nstatic DAF_item _DAFList[DAF_MAX_NUM] = {0};\n\
void __attribute__((constructor)) registerDAF()\n\
{\n\
    DAF_item item;\n\
    int i = 0;\n\n\
"
context = context + context1

pattern = re.compile(r"DAF_(\S+).h")
for i in range(0, len(listglob)):
    match = pattern.match(listglob[i])
    context = context + "    item = get" + (match.groups())[0] + "();\n" + "    _DAFList[i++] = item;\n"
    #print (match.groups())[0]
context = context + "}\n"
fileHandle.write(context)
fileHandle.close()
print "register.g has been generated!"
'''
