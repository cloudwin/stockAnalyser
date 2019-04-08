#!/usr/bin/python

print "Start to fetch data"
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
sys.path.append("..")
sys.path.append(".")
from fileLoc import *

BEGIN = 2005
def fetchAllData( index ):
    stockIndex = "%(stock)06d"%{'stock':index}
    j = 0
    currentTime = time.localtime(time.time())
    t = currentTime.tm_year
    i = t
    checkTimeFile = STATUS_DIR + stockIndex + '.check'
    try:
        with open(checkTimeFile, 'r') as checkTimeFileHandle:
            dateRecord = checkTimeFileHandle.read()
        if len(dateRecord) != 0:
            if dateRecord == str(t) + '-' + str(currentTime.tm_mon) + '-' + str(currentTime.tm_mday):
                print stockIndex + ' has already been fetched today, skip.'
                return
    except IOError: pass

    filename = DATA_DIR + stockIndex + '.csv'
    #if os.path.exists(checkTimeFile):
    #    print stockIndex + ' has already been fetched, skip.'
    #    return
    nostockcheck = STATUS_DIR + stockIndex + '_none'
    if os.path.exists(nostockcheck):
        print 'No this stock, skip.'
        return
    while i >= BEGIN:
        start = "%(year)d-01-01"%{'year':i}
        end = "%(year)d-12-31"%{'year':i}
        log = '--Fetching ' + stockIndex + ' ' + str(i)
        print log
        confirmFile = STATUS_DIR + stockIndex + '_' + str(i) + '.csv'
        if os.path.exists(confirmFile) and t != i:
            print '----Already fetched, skip.'
            i = i - 1
            continue
        df = pd.DataFrame()
        try:
            pauseTime = random.uniform(0.1, 2.0)
            print 'PauseTime:' + str(pauseTime)
            df = ts.get_h_data(stockIndex, start, end, pause = pauseTime, retry_count = 100, ascend = True, autype = 'hfq')
        #except BaseException:
        except ZeroDivisionError:
            print ''
            print 'No this stock, skip.'
            os.mknod(nostockcheck)
            return
        except urllib2.HTTPError, e:
            if e.code == 456:
                st = 360 + 60 * j
                print '456 error, sleep ' + str(st)
                time.sleep(st)
                j = j + 1
                continue
        #except BaseException:
        #    print sys.exc_info()
        print ''
        #if the data of the latest year is empty, it means the stock doesn't exist.
        if i == t and df.empty:
            print 'No this stock, skip'
            os.mknod(nostockcheck)
            return
        df.to_csv(confirmFile)
        i = i - 1
        print '--Done.'
    #merge all files
    i = BEGIN
    k = 0
    while i < t + 1:
        confirmFile = STATUS_DIR + stockIndex + '_' + str(i) + '.csv'
        tf = pd.read_csv(confirmFile)
        if k == 0:
            if not tf.empty:
                k = 1
                tf.to_csv(filename, index = False)
            else:
                i = i + 1
                continue
        else:
            tf.to_csv(filename, mode = 'a', index = False, header = None)
        i = i + 1
    #os.mknod(checkTimeFile)
    try:
        with open(checkTimeFile, 'w') as checkTimeFileHandle:
            dateRecord = checkTimeFileHandle.write(str(t) + '-' + str(currentTime.tm_mon) + '-' + str(currentTime.tm_mday))
    except IOError: pass
    
    print '--Merge over.'

#check download status directory
if not os.path.exists(STATUS_DIR):
    os.mkdir(STATUS_DIR)

print 'Get ShenZhen stocks...'
for i in range(1, 2941):
    fetchAllData(i)
print 'ShenZhen data is done!'
print 'Get ChangYeBan stocks...'
for i in range(300000, 300761):
    fetchAllData(i)
print 'ChangYeBan data is done'
print 'Get Shanghai stocks...'
for i in range(600000, 604000):
    fetchAllData(i)
print 'Shanghai data is Done'



#df = ts.get_h_data('002337', start = '2018-01-01')
#df.to_csv('./002337.csv')
