#!/usr/bin/python

print "Start to simulate the process."

#shenzhen (000001, 002940)
#cyb      (300000, 300760)
#shanghai (600000, 603999)

import ctypes
from ctypes import *
import os
import time
import pandas as pd
import sys
import datetime
import re
INVALID_DATE = datetime.datetime.strptime('1999-12-31', '%Y-%m-%d').date()

#the main process:
#1. pickup data, query stock from DAF, and buy the stock on the next day
#2. input stock index and data to DAF, and check whether sell the stock on the next day
#3. simulate the whole process, and check the yield.

#pattern 1: FIFO
#stockSet = [[1,2940], [300000, 300760], [600000, 603999]]
checkStartTime = datetime.datetime.now()
START_DATE = datetime.datetime.strptime('2005-01-01', '%Y-%m-%d').date()
END_DATE = datetime.date.today()
marketMask = 7
checkScore = 0
withdraw = 0
argc = len(sys.argv)
#if argc !=2  and argc != 4 and argc != 5 and argc != 6:
if argc < 4:
    print "Usage: datamine.py DAF_NAME START_DATE(yyyy-mm-dd) END_DATE(yyyy-mm-dd) [mask=:1 for sz, b:10 for cy, b:100 for sh] [score=1/0]"
    exit(1)
dafName = sys.argv[1]
#if argc == 4 or argc == 5:
START_DATE = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d').date()
END_DATE = datetime.datetime.strptime(sys.argv[3], '%Y-%m-%d').date()
for i in range(4, argc):
    pattern = re.compile(r"(\S+)=(\d+)")
    match = pattern.match(sys.argv[i])
    if (match.groups())[0] == 'mask':
        marketMask = int((match.groups())[1])
    elif (match.groups())[0] == 'score':
        checkScore = int((match.groups())[1])
    elif (match.groups())[0] == 'withdraw':
        withdraw = int((match.groups())[1])
    else:
        print "Usage: datamine.py DAF_NAME START_DATE(yyyy-mm-dd) END_DATE(yyyy-mm-dd) [mask=:1 for sz, b:10 for cy, b:100 for sh] [score=1/0]"
        exit(1)

#if argc == 5:
#    marketMask = int(sys.argv[4])
print 'Simulating from ' + START_DATE.strftime('%Y-%m-%d') + ' to ' + END_DATE.strftime('%Y-%m-%d') + ' mask = ' + str(marketMask) + ' score = ' + str(checkScore)

testDate = START_DATE
hold = 0

buyDate = INVALID_DATE
sellDate = None
totalOMoney = 2000 * 10000
totalMoney = totalOMoney
stockScore = [0] * 604000
tmpHold = 0
score = -1

#load c library
ll = ctypes.cdll.LoadLibrary
lib = ll("./csrc/libbuyer.so")
createDAF = lib.createDAF
createDAF.restype = c_bool
#create DAF
print 'Create DAF is ' + str(createDAF(dafName, marketMask, checkScore))
buy = lib.buy
buy.restype = c_int
sell = lib.sell
sell.restype = c_char_p
logfile = lib.logfile
profit = lib.profit
profit.restype = c_int

win = 0
lose = 0
gain = 0
#we have a score for each stock, get score from DAF.buy, and choose the best one to buy really
while testDate != END_DATE:
    checkStartTimeOne = datetime.datetime.now()
    #print 'Checking ' + testDate.strftime('%Y-%m-%d')
    if hold == 0: #we don't have any stock, wanna buy~
        hold = buy(testDate.strftime('%Y-%m-%d'))
        #print 'Buy? ' + str(hold)
        #if hold != 0:
            #print 'Buy:' + "%(stock)06d"%{'stock':hold}
    else: #we wanna sell~
        if sellDate == None:
            sellDate = sell(testDate.strftime('%Y-%m-%d'))
            if sellDate != None:
        #if sell(testDate.strftime('%Y-%m-%d')) == True:
            #print 'Sell:' + "%(stock)06d"%{'stock':hold}
                newMoney = profit(totalMoney);
                if withdraw == 0:
                    if newMoney > totalMoney:
                        win = win + 1
                    else:
                        lose = lose + 1
                    totalMoney = newMoney
                    print 'Total money = ' + str(totalMoney)
                else:
                    if newMoney > totalMoney:
                        win = win + 1
                        if newMoney > totalOMoney:
                            gain = gain + newMoney - totalOMoney
                            totalMoney = totalOMoney
                        else:
                            totalMoney = newMoney
                    else:
                        lose = lose + 1
                        totalMoney = newMoney
                    if totalMoney != 0:
                        print 'Total money = ' + str(totalMoney) + ', Gain = ' + str(gain)
        else:
            #print 'Check sell ' + sellDate
            if testDate.strftime('%Y-%m-%d') == sellDate:
                hold = 0
                sellDate = None;
    testDate = testDate + datetime.timedelta(days = 1)
    checkEndTimeOne = datetime.datetime.now()
    print 'Time: ' + str((checkEndTimeOne - checkStartTimeOne).seconds) + ' seconds'
if hold != 0:
    newMoney = profit(totalMoney)
    if newMoney > totalMoney:
        win = win + 1
    else:
        lose = lose + 1
    totalMoney = newMoney
print ''
print '----------------------------------------------------------------'
print 'Simulation is over, the total money is ' + str(totalMoney) + ', win = ' + str(win) + ', lose = ' + str(lose)
logfile('_'+ START_DATE.strftime('%Y-%m-%d') + '_' + END_DATE.strftime('%Y-%m-%d') + '_' + str(marketMask) + '_' + str(checkScore))

checkEndTime = datetime.datetime.now()
print 'Total time: ' + str((checkEndTime - checkStartTime).seconds) + ' seconds'

