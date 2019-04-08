#!/usr/bin/python

print "Start to calculate BOLL"

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

def lastDay(tf, date, stocki):
    if tf.empty:
        return INVALID_DATE
    lastDate = pd.DataFrame()
    if date == START_DATE:
        return INVALID_DATE
    while lastDate.empty:
        date = date + datetime.timedelta(days = -1)
        if date == START_DATE:
            return INVALID_DATE
        lastDate = tf[tf.date == date.strftime('%Y-%m-%d')]
    return date

def nextDay(tf, date, stocki):
    if tf.empty:
        return INVALID_DATE
    nextDate = pd.DataFrame()
    if date == END_DATE:
        return INVALID_DATE
    while nextDate.empty:
        date = date + datetime.timedelta(days = 1)
        if date == END_DATE:
            return INVALID_DATE
        nextDate = tf[tf.date == date.strftime('%Y-%m-%d')]
    return date

def calBOLL(datafile, currentBOLL, period):
    lines = datafile.iloc[:,0].size
    BOLL = 0
    UB = 0
    LB = 0
    bollLines = 0

    if currentBOLL.empty:
        BOLL = 0
        UB = 0
        LB = 0
        currentBOLL.loc[0] = [datafile.iloc[0]['date'], BOLL, UB, LB]
    else:
        bollLines = currentBOLL.iloc[:,0].size
        if lines <= bollLines:
            return currentBOLL
    numStore = []
    for k in range(bollLines, lines):
        numStore.append(datafile.iloc[k]['close'])
        if k < period - 1:
            currentBOLL.loc[k] = [datafile.iloc[k]['date'], 0, 0, 0]
            continue
        if k != period:
            numStore.pop(0)
        addSum = 0
        for kk in range(k - period + 1, k + 1):
            addSum = addSum + datafile.iloc[kk]['close']
        BOLL = addSum / period
        addSum = 0
        for kk in range(k - period + 1, k + 1):
            addSum = addSum + (datafile.iloc[kk]['close'] - BOLL) * (datafile.iloc[kk]['close'] - BOLL)
        STD = (addSum / period) ** 0.5
        UB = BOLL + 2 * STD
        LB = BOLL - 2 * STD
        currentBOLL.loc[k] = [datafile.iloc[k]['date'], BOLL, UB, LB]
    return currentBOLL
  


stockSet = [[1,2940], [300000, 300760], [600000, 603999]]
i = 0
j = 0
for i in range(0,3):
    for j in range(stockSet[i][0], stockSet[i][1] + 1):
        print("\rTrying to reach %(stock)06d."%{'stock':j}),
        BOLL = pd.DataFrame(columns = ['date', 'BOLL', 'UB', 'LB'])
        tf = readDataFile(j)
        if tf.empty:
            continue
        bollfileName = INDICATOR_DIR + "BOLL/%(stock)06d.boll"%{'stock':j}
        if os.path.exists(bollfileName):
            BOLL = pd.read_csv(bollfileName)
        print("\rCalculate BOLL for %(stock)06d."%{'stock':j})
        BOLL = calBOLL(tf, BOLL, 20)
        if not os.path.exists(INDICATOR_DIR):
            os.mkdir(INDICATOR_DIR)
        if not os.path.exists(INDICATOR_DIR + "BOLL/"):
            os.mkdir(INDICATOR_DIR + "BOLL")

        BOLL.to_csv(bollfileName, index = False)
        print 'Done.'

