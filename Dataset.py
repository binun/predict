import numpy
from Service.Utilities import Tools
from Configuration import Configuration
import os
import math
from pandas.tseries.offsets import BDay
import datetime

from _functools import reduce


class Dataset(object):
 
    def __init__(self, columns,dates,stickers):
        self.colLabels = columns 
        self.dates = dates
        self.stickers = stickers
        self.matrix = numpy.zeros ((len(stickers), len(columns), len(dates)))
    
    def mockDay(self,tm):
        
        (x,y,z) = self.matrix.shape
        newmatrix = numpy.zeros ((x,y,z+1))
        for i in range(0,x):
            for j in range(0,y):
                for k in range(0,z):
                    if k==z-1:
                        newmatrix[i,j,k] = 23.0+float(k/10)
                    else:
                        newmatrix[i,j,k] = self.matrix[i,j,k]
        self.matrix = newmatrix
                     
           
    def set(self,sticker,column,timestamp,val): # open/close... , (timestamp, depth), sticker
          
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.dates.index(timestamp)
        charact_index = self.colLabels.index(column)
        v = None
        
        if numpy.isnan(val) or numpy.isinf(val):
            v = 0
        else:
            v = val
          
        self.matrix[sticker_index,charact_index,timestamp_index] = v
        
    def get(self,sticker,column,timestamp=None,depth=1):
        
        sticker_index = self.stickers.index(sticker)
        charact_index = self.colLabels.index(column)
        
        endindex=0
        if timestamp is None:
            endindex = len(self.dates)
        else:
            endindex = self.dates.index(timestamp)
            
        if depth<0:
            startindex=0
        else:
            startindex = max(0,endindex-depth)
        #if len(self.colLabels)>1:
            #while self.matrix[sticker_index,charact_index,startindex]==0:
                #startindex=startindex+1
            
        intermediate = self.matrix[sticker_index,charact_index,startindex:endindex]
            
        if depth==1:
            return intermediate[0]
        else:
            return intermediate
        
    def getAt(self,sticker,column,timestamp=None):
        sticker_index = self.stickers.index(sticker)
        charact_index = self.colLabels.index(column)
        
        if timestamp is not None:
            timestamp_index = self.dates.index(timestamp)
        else:
            timestamp_index = len(self.dates)-1
            
#         if len(self.colLabels)>1:
#             while timestamp_index>=0 and self.matrix[sticker_index,charact_index,timestamp_index]==0.0:
#                 timestamp_index=timestamp_index-1
        
        return self.matrix[sticker_index,charact_index,timestamp_index]
    
    def timestamps(self):
        return self.dates
    
    def stickerTrade(self,sticker,timestamp):
        colnames = Configuration.columnNames
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.dates.index(timestamp)
        nonzeros=False
        for col in colnames:
            indx = self.colLabels.index(col)
            val = self.matrix[sticker_index,indx,timestamp_index]
            nonzeros=nonzeros or math.fabs(val)>0.0001
        return nonzeros
        
        
        