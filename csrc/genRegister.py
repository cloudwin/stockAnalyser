#!/usr/bin/python

import os
import glob
import re
import sys
sys.path.append("..")
from fileLoc import *

with open("./fileLoc.h", "w") as filehead:
    filehead.write('//Auto generated file\n')
    filehead.write('#define LOG_DIR "' + LOG_DIR + '"\n')
    filehead.write('#define DATA_DIR "' + DATA_DIR + '"\n')
    filehead.write('#define STATUS_DIR "' + STATUS_DIR + '"\n')
    filehead.write('#define INDICATOR_DIR "' + INDICATOR_DIR + '"\n')

print "Scan all DAF head files..."
dirglob = []
listglob = []
dirglob = glob.glob(r"./*")
for i in dirglob:
    if os.path.isdir(i):
        listglob = listglob + glob.glob(i + "/DAF_*.h")

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

try:
    listHandle = open("../DAF.list", "w")
except IOError:
    print "Can't open DAF.list"

pattern = re.compile(r"./(\S+)/DAF_(\S+).h")
for i in range(0, len(listglob)):
    match = pattern.match(listglob[i])
    context = context + "    item = get" + (match.groups())[0] + "();\n" + "    _DAFList[i++] = item;\n"
    listHandle.write((match.groups())[0])
    listHandle.write("\n")
    #print (match.groups())[0]
context = context + "}\n"
listHandle.close()
fileHandle.write(context)
fileHandle.close()
print "register.g has been generated!"
