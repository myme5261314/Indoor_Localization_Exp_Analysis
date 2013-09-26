#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2013-9-26

@author: peng
'''

import os,json,re,datetime


if __name__ == '__main__':
    js = json.load(open('/home/peng/601_1.12,2.55_2013-09-23-111243.json'))
    jso = js.copy()
    print len(jso['RSSILists'])
    removelist = []
    for apindex,ap in enumerate(jso['RSSILists']):
        if not re.match(r'AP\d', ap['apName']):
            removelist.append(ap)
        else:
            print ap['apName']
    for ap in removelist:
        jso['RSSILists'].remove(ap)
        
    startTime = datetime.datetime.strptime(jso['startTime'],'%Y-%m-%d  %H:%M:%S')
    startTime += datetime.timedelta(minutes=18)
    jso['startTime'] = startTime.strftime('%Y-%m-%d  %H:%M:%S')
    jso['duringTime'] = str(30*60)
    for ap in jso['RSSILists']:
        ap['RSSI'] = ap['RSSI'][18*60:48*60]
        print len(ap['RSSI'])
    print len(jso['RSSILists'])
    json.dump(jso,open('/home/peng/1.json','w'))
