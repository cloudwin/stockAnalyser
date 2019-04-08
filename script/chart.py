#!/usr/bin/python
#shenzhen (000001, 002940)
#cyb      (300000, 300760)
#shanghai (600000, 603999)

import sys
import os
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import pandas as pd
import datetime

def readDataFile(fileName):
    context = []
    date = []
    money = []
    try:
        with open(fileName, 'r') as f:
            context = f.readlines()
            for i in range(0, len(context)):
                s = context[i].split(' ')
                date.append(datetime.datetime.strptime(s[0], '%Y-%m-%d'))
                money.append(int(float(s[1])))
            return [date, money]
    except IOError:
        print "Can't open " + fileName
        return []

#main process: load all data from files, and display them in one chart
argc = len(sys.argv)

CA = plt.figure(num='Chart Analyser', dpi=100, figsize = (12,8))
ax = CA.add_subplot(1,1,1)
#plt.subplot(111, facecolor = '#000000')
ax.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d'))
#ax.xaxis.set_major_locator(mdate.DayLocator())
ax.xaxis.set_major_locator(mdate.MonthLocator())

colors = ('white', 'black', 'red', 'yellow', 'blue', 'green', 'fuchsia', 'cyan')
for i in range(1, argc):
    data = readDataFile(sys.argv[i])
    if len(data) != 0:
        ax.plot(data[0], data[1], color = colors[i])
        doc = plt.scatter(data[0], data[1], color = colors[i])

plt.xticks(rotation=60)
plt.show()
plt.close()
