#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2013-9-24

@author: peng
'''

import datetime
import json
import os
import re
import matplotlib.pyplot as plt
import numpy as np
import pylab
from IPython.parallel.controller.scheduler import numpy

class ExperimentData():
    def __init__(self, inputpath):
        self.inputpath = inputpath
        self.ptlist = os.listdir(inputpath + '/RawData')  # The point list
        self.ptlist.sort(key=lambda x: int(x.split(',')[0]) + 100 * int(x.split(',')[1]))
        self.aplist = []
        self.recordlist = []
        print self.ptlist
        self.data = dict()
        self.startTime = None
        self.endTime = None
    def load(self):
        for pt in self.ptlist:
            print pt
            self.data[pt] = dict()
            ptpath = self.inputpath + '/RawData/' + pt + '/'
            recordlist = os.listdir(ptpath)
            for i, record in enumerate(recordlist):
                js = json.load(open(ptpath + record))
                if i == 1:
                    self.startTime = datetime.datetime.strptime(js['startTime'], '%Y-%m-%d  %H:%M:%S')
                elif i == len(recordlist) - 1:
                    self.endTime = datetime.datetime.strptime(js['startTime'], '%Y-%m-%d  %H:%M:%S') + datetime.timedelta(seconds=int(js['duringTime']))
                print js.keys()
                print self.startTime, self.endTime
                for rssirecord in js['RSSILists']:
                    if re.match(r'AP\d',rssirecord['apName']):
                        apName = rssirecord['apName']
                        if apName not in self.aplist:
                            self.aplist.append(apName)
                        rssidata = rssirecord['RSSI']
                        if self.data[pt].has_key(apName):
                            self.data[pt][apName].extend(rssidata)
                        else:
                            self.data[pt][apName] = rssidata
#                 print self.data[pt]
        self.aplist.sort()
    def draw(self):
        for pt in self.ptlist:
            plt.figure()
            plt.title(pt)
            for i,apname in enumerate(self.aplist):
                print apname
                plt.subplot(2,2,i+1)
                p,r = np.histogram(self.data[pt][apname],120)
                print type(p)
                index = p.max()
                pylab.hist(self.data[pt][apname],120,range=(-120,0),
                            label=[apname+str(index)]
                            )
                plt.legend()
        plt.show()
        

if __name__ == '__main__':
    e = ExperimentData('/home/peng/experiments/Wifi_Indoor_Localization/2.correct_12h_data/319/2013-07-09/')
    e.load()
    print e.aplist
    e.draw()
        
        
