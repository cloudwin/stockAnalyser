#!/usr/bin/python

print "Start to calculate KDJ"

#shenzhen (000001, 002940)
#cyb      (300000, 300760)
#shanghai (600000, 603999)

import tushare as ts
import os
import time
import pandas as pd
import sys
import urllib2
import random
import datetime
sys.path.append("..")
sys.path.append(".")
from fileLoc import *

INVALID_DATE = datetime.datetime.strptime('1999-12-31', '%Y-%m-%d').date()

def readDataFile(sindex):
    stockIndex = "%(stock)06d"%{'stock':sindex}
    logName = DATA_DIR + stockIndex + '.csv'
    try:
        tf = pd.read_csv(logName)
    except IOError:
        return pd.DataFrame()
    return tf

def checkLowAndHigh(period, newHigh, newLow):
    if not hasattr(checkLowAndHigh, 'store'):
        checkLowAndHigh.store = [[newHigh, newLow]]
        return [newHigh, newLow]
    i = len(checkLowAndHigh.store)
    highi = 0
    lowi = 65536
    if i < period:
        checkLowAndHigh.store.append([newHigh, newLow])
        for i in range(0, i + 1):
            if checkLowAndHigh.store[i][0] > highi:
                highi = checkLowAndHigh.store[i][0]
            if checkLowAndHigh.store[i][1] < lowi:
                lowi = checkLowAndHigh.store[i][1]

    else:
        for i in range(0, period - 1):
            checkLowAndHigh.store[i] = checkLowAndHigh.store[i + 1]
            if checkLowAndHigh.store[i][0] > highi:
                highi = checkLowAndHigh.store[i][0]
            if checkLowAndHigh.store[i][1] < lowi:
                lowi = checkLowAndHigh.store[i][1]
        checkLowAndHigh.store[period -1] = [newHigh, newLow]
        if newHigh > highi:
            highi = newHigh
        if newLow < lowi:
            lowi = newLow
    #print '-----------------------------------------' + str(highi) + ',' + str(lowi)
    #for i in range(0, len(checkLowAndHigh.store)):
    #    print str(checkLowAndHigh.store[i][0]) + ',' + str(checkLowAndHigh.store[i][1])
    return [highi, lowi]

def calKDJ(datafile, currentKDJ):
    lines = datafile.iloc[:,0].size
    kdjLines = 0
    if currentKDJ.empty:
        #Ln = datafile.iloc[0]['low']
        #Hn = datafile.iloc[0]['high']
        preK = 50.0
        preD = 50.0
    else:
        kdjLines = currentKDJ.iloc[:,0].size
        if lines <= kdjLines:
            return currentKDJ
        '''
        lastDate = currentKDJ.iloc[kdjLines - 1]['date']
        i = lines - 1
        while i >= 0:
        #for i in range(1, lines):
            if datafile.iloc[i]['date'] == lastDate:
                break
            i = i - 1
        if i < 0:
            print "Fatal error: can't find " + lastDate
            return currentKDJ
        '''
        preK = currentKDJ.iloc[kdjLines - 1]['K']
        preD = currentKDJ.iloc[kdjLines - 1]['D']
        for i in range(kdjLines - 8, kdjLines):
            l = datafile.iloc[i]['low']
            h = datafile.iloc[i]['high']
            checkLowAndHigh(n, h, l)
    for k in range(kdjLines, lines):
        Cn = datafile.iloc[k]['close']
        low = datafile.iloc[k]['low']
        high = datafile.iloc[k]['high']
        list = checkLowAndHigh(n, high, low)
        Hn = list[0]
        Ln = list[1]
        if k == 0 or Hn == Ln:
            RSV = 0
        else:
            RSV = (Cn - Ln) / (Hn -Ln) * 100
        K = (2 * preK / 3) + (RSV / 3)
        D = (2 * preD / 3) + (K / 3)
        J = (3 * K) - (2 * D)
        KDJ.loc[k] = [tf.iloc[k]['date'], K, D, J]
        preK = K
        preD = D
    return currentKDJ

stockSet = [[1,2940], [300000, 300760], [600000, 603999]]
i = 0
j = 0
n = 9

for i in range(0,3):
    for j in range(stockSet[i][0], stockSet[i][1] + 1):
        print("\rTrying to reach %(stock)06d."%{'stock':j}),
        KDJ = pd.DataFrame(columns = ['date', 'K', 'D', 'J'])
        tf = readDataFile(j)
        if tf.empty:
            continue
        kdjfileName = INDICATOR_DIR + "KDJ/%(stock)06d.kdj"%{'stock':j}
        if os.path.exists(kdjfileName):
            KDJ = pd.read_csv(kdjfileName)
        print("\rCalculate KDJ for %(stock)06d."%{'stock':j})
        
        KDJ = calKDJ(tf, KDJ)
        if not os.path.exists(INDICATOR_DIR):
            os.mkdir(INDICATOR_DIR)
        if not os.path.exists(INDICATOR_DIR + "KDJ/"):
            os.mkdir(INDICATOR_DIR + "KDJ")
        KDJ.to_csv(kdjfileName, index = False)
        print 'Done.'

