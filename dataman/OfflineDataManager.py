import os
import pandas
from dataman import DataManager
import numpy
from Service.Utilities import Tools
import datetime
from Configuration import Configuration
import math
class OfflineDataManager(DataManager.DataManager):
    
    def __init__(self, dsource):
        super().__init__(dsource)
        
    def fetchAllData(self):
        
        if len(Configuration.limitds)==0:
            for file in os.listdir(self.datasource):
                stickername = os.path.splitext(file)[0]
                if len(self.extension)==0:
                    self.extension=os.path.splitext(file)[1]
                self.stickers.append(stickername)
        else:
            df=pandas.read_csv("{0}_stickers.csv".format(Configuration.limitds),header=None,parse_dates=True)
            self.extension=".TXT"
            for val in df.values:
                fullname = os.path.join(os.getcwd(), self.datasource, val[0] +self.extension)
                if os.path.exists(fullname):
                    self.stickers.append(val[0])    
            del df
            
            
        print("Downloaded {0} stickers:".format(len(self.stickers)))
            
        s=set()
        
        for sticker in self.stickers:            
            #if 'sandp' in self.datasource or :  
            m=self.fetchSPStickerData(sticker)
            #else:
                #m=self.fetchStickerData(sticker)
                
                
            if m is not None:
                self.rawData.append(m)
                for ld in m.keys():
                    s.add(ld)
        self.datesList = list(s)
        self.datesList.sort(key=lambda x: datetime.datetime.strptime(x,'%Y-%m-%d'))
        del s      
                    
        print("Data collected: {0} records, {1} timestamps".format(len(m),len(self.datesList)))
        
    def fetchStickerData(self,sticker):
        print("Downloading sticker {0} ".format(sticker))
        fullname = os.path.join(os.getcwd(), self.datasource, sticker +self.extension)
        df = None
        try:
            df = pandas.read_csv(fullname,header=None,float_precision='high')
        except:
            print('No history so far')
            return
                        
        
        np={}
        histdata=df.values
        for recnum in range(0,len(histdata)):
            date = str(histdata[recnum,1])
            fancydate = '{0}-{1}-{2}'.format(date[0:4],date[4:6],date[6:8])
            
            values=[]
            for i in range(0,5):
                rel=0.0
                if recnum>0 and histdata[recnum-1,i+2]!=0:
                    rel=Tools.cancelNan(100.0*(histdata[recnum,i+2]-histdata[recnum-1,i+2])/histdata[recnum-1,i+2])
                values.append(rel)
            np[fancydate] = values
                
        return np
    
    def fetchSPStickerData(self,sticker):
        year = Configuration.simyear
        print("Downloading sticker {0} ".format(sticker))

        fullname = os.path.join(os.getcwd(), self.datasource, sticker + self.extension)
        df = None
        try:
            df = pandas.read_csv(fullname,sep='\s+',header=None,float_precision='high')
        except:
            print('No history so far')
            return
                            
        hist=df.values
        histdata=[]
        fdIndex=-1
        i=0
        for histitem in hist:
            date = str(int(histitem[0]))
            y = date[0:4]
            m=date[4:6]
            if len(year)>1:
                if y==year:
                    if fdIndex<0 and m=='01' and date[6]=='0':
                        indices = numpy.where(hist==histitem)
                        fdIndex=i
                    histdata.append(histitem)
                i=i+1
            else:
                histdata.append(histitem)
        
        if fdIndex>=100:
            totaldata=[]
            for idx in range(fdIndex-100,fdIndex):
                totaldata.append(hist[idx])
            for histitem in histdata:
                totaldata.append(histitem)
            
            histdata = totaldata
            Configuration.seloffset = 100
                    
        np={}
        
        for recnum in range(0,len(histdata)):
            date = str(int(histdata[recnum][0]))
            fancydate = '{0}-{1}-{2}'.format(date[0:4],date[4:6],date[6:8])
            values=[]
            for i in range(0,5):
                rel=0.0
            
                if recnum>0 and histdata[recnum-1][i+1]!=0:
                    v=histdata[recnum][i+1]
                    pv= histdata[recnum-1][i+1]
                    delta= (v-pv)/pv
                    if v<3 or pv<3 or math.fabs(delta)>40:
                        delta=0
                    rel=Tools.cancelNan(100.0*delta)
                values.append(rel)
            np[fancydate] = values
            
        del histdata
        
        origl = list(np.items())
        l = len(origl)
        np = dict(origl[0:(l-10)])
        
        return np
            
        
        
        
            
            
        