import time
import os
from datetime import date
from Configuration import Configuration

from Dataset import Dataset
import numpy
from pandas.tseries.offsets import BDay
import pandas
from Service.Utilities import Tools
import math

class DataManager():

    datesList=list()
    today=date.today()
    maxrows=0
    
    kind=''
    

    def __init__(self, dsource):
        
        self.stickers=[]
        self.rawData=[]
        self.datasource=dsource
        self.dataset = None
        self.dirty = True
        self.tomorrow = None
        self.extension=''
            
        self.fetchAllData()
        print("Overall: {0} timestamps".format(len(self.datesList)))
        
        ts = pandas.Timestamp(self.datesList[-1])+BDay(1)
        self.tomorrow = ts.strftime('%Y-%b-%d')
        self.datesList.append(self.tomorrow)
        
        if self.dataset is None:
            self.dataset = self.getDataset()
        
    def mockDay(self):
        ts = pandas.Timestamp(self.datesList[-1])+BDay(1)
        tm = ts.strftime('%Y-%b-%d')
        self.datesList.append(tm)
        self.dataset.mockDay(tm)
    
    def switchedMonth(self,timestamp):
        ti = None
        try:
            ti=self.datesList.index(timestamp)
        except:
            return False
        
        if ti<10:
            return False
        prev_day = self.datesList[ti-1]
        cur_month = timestamp.split('-')[1]
        prev_month = prev_day.split('-')[1]
        return (cur_month!=prev_month)
        
    def getDataset(self):
        
        if self.dirty:    
            ds = Dataset(Configuration.columnNames, self.datesList, self.stickers)
            for si,stickerdata in enumerate(self.rawData):
                sticker = self.stickers[si]
                for timestamp,valvector in stickerdata.items():
                    for ci in range(0,len(Configuration.columnNames)):
                        val = valvector[ci]
                        charact = Configuration.columnNames[ci]
                        ds.set(sticker,charact,timestamp, val)
            self.dataset = ds
            self.dirty=False
        return self.dataset
            
    def fetchAllData(self):
        pass   
    
    def dailyAccumulatedRaw(self,until,offset,skipdict):
        accums=0
        if offset<=0:
            offset=Configuration.seloffset
        
        for indx in range(offset,self.datesList.index(until)):
            cts = self.datesList[indx]
      
            deltas = [self.getAt(sticker,'close',cts) for sticker in self.stickers]
            incr=numpy.average(deltas)
            
            
            accums=accums+incr
            
        return accums
    
    def addDays(self,timestamp,numdays):
        idx = self.datesList.index(timestamp)
        
        idx=idx+numdays
        
        if idx<0:
            idx=0
        if idx>len(self.datesList)-1:
            idx =len(self.datesList)-1
        return self.datesList[idx]
    
    def getAt(self,sticker,column,timestamp):
        return self.dataset.getAt(sticker, column, timestamp)
    
    def stickerActive(self,sticker,timestamp):
        return self.dataset.stickerTrade(sticker, timestamp)
        
            
                
                
        
         
    
    
            