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
import time
from matplotlib.colors import NP_CLIP_OUT

class ExperimentData():
    def __init__(self, inputpath):
        self.inputpath = inputpath
        self.datadir = '/RawData/'
        # self.data[ptindex][recordindex][apindex][dataindex] = rssi
        self.ptlist = []
        self.aplist = []  # The ap list
        self.records = 0
        self.periodtime = 0
        self.scenery = 0
        self.freq = 0
        self.startTime = None
        self.endTime = None
        self.data = None
        self.getExperimentProperty()
        
    def getExperimentProperty(self):
        self.ptlist = os.listdir(self.inputpath + self.datadir)  # The point list
        self.ptlist.sort(key=lambda x: float(x.split(',')[0]) + 100 * float(x.split(',')[1]))
        self.records, self.aplist, self.periodtime, self.scenery, self.freq, self.startTime, self.endTime \
            = self.assertRecordSame()
        
    def assertRecordSame(self):
        records = -1
        for ptindex, pt in enumerate(self.ptlist):
            # Assert record num to be same in each pt
            ptpath = self.inputpath + self.datadir + pt
            recordlist = os.listdir(ptpath)
            l = len(recordlist)
            if l != records and records != -1:
                raise Exception('the record file number is not same with the previous one in path\n%s', ptpath)
            else:
                records = l
            # Assert apnum to be same in each record
            aplist = []
            duringTime = -1
            scenery = ''
            freq = -1
            for recordindex, record in enumerate(recordlist):
                cmpaplist = []
                recordpath = ptpath + '/' + record
                js = json.load(open(recordpath))
                # Assert duringTime
                if int(js['duringTime']) != duringTime and duringTime != -1:
                    raise Exception('the duringTime is not same with the previous one in path\n%s', recordpath)
                else:
                    duringTime = int(js['duringTime'])
                # Assert scenery
                if js['scenery'] != scenery and scenery != '':
                    raise Exception('the scenery is not same with the previous one in path\n%s', recordpath)
                else:
                    scenery = js['scenery']
                # Assert freq
                if int(js['freq']) != freq and freq != -1:
                    raise Exception('the freq is not same with the previous one in path\n%s', recordpath)
                else:
                    freq = int(js['freq'])
                
                if ptindex == 0 and recordindex == 0:
                    startTime = datetime.datetime.strptime(js['startTime'], '%Y-%m-%d  %H:%M:%S')
                if ptindex == len(self.ptlist)-1 and recordindex == records-1:
                    endTime = datetime.datetime.strptime(js['startTime'], '%Y-%m-%d  %H:%M:%S')\
                                + datetime.timedelta(seconds=duringTime)
                
                jslist = js['RSSILists']
                for aprecord in jslist:
                    if re.match(r'AP\d', aprecord['apName']):
                        if aprecord['apName'] not in cmpaplist:
                            cmpaplist.append(aprecord['apName'])
                cmpaplist.sort()
                if cmpaplist != aplist and aplist != []:
                    raise Exception('the apList is not same with the previous file in path\n%s', recordpath)
                else:
                    aplist = cmpaplist
        return l, aplist, duringTime, scenery, freq, startTime, endTime

    def load(self):
        self.datashape = (len(self.ptlist), self.records , len(self.aplist), self.periodtime * self.freq)
        self.data = np.ndarray(self.datashape)
        for ptindex, pt in enumerate(self.ptlist):
            ptpath = self.inputpath + self.datadir + pt
            recordlist = os.listdir(ptpath)
            for recordindex, record in enumerate(recordlist):
                recordpath = ptpath + '/' + record
                js = json.load(open(recordpath))
                rssilists = js['RSSILists']
                for rssi in rssilists:
                    apname = rssi['apName']
                    try:
                        apindex = self.aplist.index(apname)
                    except ValueError:
                        continue
                    datalist = rssi['RSSI']
                    self.data[ptindex, recordindex, apindex] = np.array(datalist)
    def draw(self):
        for ptindex, pt in enumerate(self.ptlist):
            plt.figure(pt + ': ' + self.startTime.strftime('%x %X') + ' - ' + self.endTime.strftime('%x %X'))
            print self.startTime.strftime('%x %X') + ' - ' + self.endTime.strftime('%x %X')
            for apindex, apname in enumerate(self.aplist):
                plt.subplot(2, 2, apindex + 1)
                plt.title(apname)
                for recordindex in range(self.records):
                    period = self.datashape[-1]
                    for i in range(period / 60):
                        times, r = np.histogram(self.data[ptindex, recordindex, apindex, i * 60:i * 60 + 59], 120, range=(-120, 0), density=True)
                        indexdict = dict()
                        for i, j in zip(r, times):
                            indexdict[i] = j
                        sortindexlist = sorted(indexdict.items(), key=lambda x: x[1], reverse=True)
#                         print sortindexlist
#                         print sortindexlist[0][1] + sortindexlist[1][1] + sortindexlist[2][1]
                        maxindex = str(sortindexlist[0][0])
                        secondindex = str(sortindexlist[1][0])
                        pylab.plot(range(-120, 0), times, label=apname + ':' + maxindex + '|' + secondindex)
#                         pylab.hist(self.data[ptindex, recordindex, apindex, i * 60:i * 60 + 59], 120, range=(-120, 0),
#                                     label=[apname + ':' + maxindex + '|' + secondindex]
#                                     )
                plt.legend()
        plt.show()
        

if __name__ == '__main__':
    s = time.time()
    inputpath = '/home/peng/experiments/Wifi_Indoor_Localization/' + \
                '5.pattern_analysis_data_v2_601/full_fingerprint/3.601_fullfingerprint_5min_22'
#                 '5.pattern_analysis_data_v2_601/full_fingerprint/1.601_fullfingerprint_5min_12'
#     inputpath = '/home/peng/'
    e = ExperimentData(inputpath)
    e.load()
    e.draw()
    end = time.time()
    print end - s
#     print e.data
        
