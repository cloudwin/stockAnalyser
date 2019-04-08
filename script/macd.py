#!/usr/bin/python

print "Start to calculate MACD"

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

def calMACD(datafile, currentMACD):
    lines = datafile.iloc[:,0].size
    EMA12 = 0
    EMA26 = 0
    DIF = 0
    DEA9 = 0
    macd = 0
    EMA12t = 0
    DEA9t = 0
    k = 1
    macdLines = 1

    if currentMACD.empty:
        EMA12 = datafile.iloc[0]['close']
        EMA26 = EMA12
        DIF = EMA12 - EMA26
        macd = 2 * (DIF - DEA9)
        currentMACD.loc[0] = [datafile.iloc[0]['date'], DIF, DEA9, macd, EMA12, EMA26]
    else:
        macdLines = currentMACD.iloc[:,0].size
        if lines <= macdLines:
            return currentMACD
        '''
        lastDate = currentMACD.iloc[macdLines - 1]['date']
        i = lines - 1
        while i >= 0:
        #for i in range(1, lines):
            if datafile.iloc[i]['date'] == lastDate:
                break
            i = i - 1
        if i < 0:
            print "Fatal error: can't find " + lastDate
            return currentMACD
        '''
        EMA12 = currentMACD.iloc[macdLines - 1]['EMA12']
        EMA26 = currentMACD.iloc[macdLines - 1]['EMA26']
        DEA9 = currentMACD.iloc[macdLines - 1]['DEA']

    for k in range(macdLines, lines):
        EMA12t = datafile.iloc[k]['close'] * 0.1538 + EMA12 * 0.8462
        EMA26t = datafile.iloc[k]['close'] * 0.0741 + EMA26 * 0.9259
        EMA12 = EMA12t
        EMA26 = EMA26t
        DIF = EMA12t - EMA26t
        DEA9t = 0.2 * DIF + 0.8 * DEA9
        DEA9 = DEA9t
        macd = (DIF - DEA9t) * 2
        currentMACD.loc[k] = [datafile.iloc[k]['date'], DIF, DEA9, macd, EMA12, EMA26]
    return currentMACD
  


stockSet = [[1,2940], [300000, 300760], [600000, 603999]]
i = 0
j = 0
for i in range(0,3):
    for j in range(stockSet[i][0], stockSet[i][1] + 1):
        print("\rTrying to reach %(stock)06d."%{'stock':j}),
        MACD = pd.DataFrame(columns = ['date', 'DIF', 'DEA', 'MACD', 'EMA12', 'EMA26'])
        tf = readDataFile(j)
        if tf.empty:
            continue
        macdfileName = INDICATOR_DIR + "MACD/%(stock)06d.macd"%{'stock':j}
        if os.path.exists(macdfileName):
            MACD = pd.read_csv(macdfileName)
        print("\rCalculate MACD for %(stock)06d."%{'stock':j})
        MACD = calMACD(tf, MACD)
        if not os.path.exists(INDICATOR_DIR):
            os.mkdir(INDICATOR_DIR)
        if not os.path.exists(INDICATOR_DIR + "MACD/"):
            os.mkdir(INDICATOR_DIR + "MACD")

        MACD.to_csv(macdfileName, index = False)
        print 'Done.'

