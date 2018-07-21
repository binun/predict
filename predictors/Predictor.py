import numpy
from Configuration import Configuration
from Service.Utilities import Tools
from Dataset import Dataset

import traceback
import time
import math
from numpy import dtype, int8, average
import pandas
import gc
import os

class Predictor(object):
   
    def __init__(self, name, datamanager,hist=-1,context=None):
    
        self.dataManager = datamanager
            
        self.timestamps = datamanager.datesList
        self.fuslen = Configuration.fushistlen
        self.maxhistlen = Configuration.maxhistlen
    
        self.stickers = []
        self.name=name
        self.preprocessed=False
        self.context=context
        
        if hist>0:
            self.histlen = hist
        else:
            self.histlen = self.maxhistlen
            
        self.startOffset = self.histlen
        self.predictorList = None
    
        self.timestamps = datamanager.datesList
        self.stickers = datamanager.stickers
        c=len(self.stickers)
        r = len(self.timestamps)

        self.skips = [[0 for i in range(r)] for j in range(c)]
        self.hits = [[0 for i in range(r)] for j in range(c)]
        self.predictions = [[0 for i in range(r)] for j in range(c)]
        self.udw = numpy.ones( (c,r,2) )
        
        self.confidences = [[0 for i in range(r)] for j in range(c)]
        self.negconfidences = [[0 for i in range(r)] for j in range(c)]
          
        
    def save(self):
        
        sn = self.dataManager.stickers.index(self.stickers[0])
        
        skips = numpy.array(self.skips)
        hits = numpy.array(self.hits)
        predictions = numpy.array(self.predictions)
        udw = numpy.array(self.udw)
        confs = numpy.array(self.confidences)
        nconfs = numpy.array(self.negconfidences)
        
        numpy.savetxt(self.name+'_skips.txt',skips[sn],fmt='%d')
        numpy.savetxt(self.name+'_hits.txt',hits[sn],fmt='%d')
        numpy.savetxt(self.name+'_preds.txt',predictions[sn],fmt='%d')
        #numpy.savetxt(self.name+'_udw.txt',udw,fmt='%d')
        numpy.savetxt(self.name+'_conf.txt',confs[sn],fmt='%f')
        numpy.savetxt(self.name+'_nconf.txt',nconfs[sn],fmt='%f')
        
        
    def restore(self):
        hits = numpy.loadtxt(self.name+'_hits.txt',dtype=int)
        skips = numpy.loadtxt(self.name+'_skips.txt',dtype=int)
        predictions = numpy.loadtxt(self.name+'_preds.txt',dtype=int)
        #udw = numpy.loadtxt(self.name+'_udw.txt',dtype=int)
        confs = numpy.loadtxt(self.name+'_conf.txt',dtype=float)
        nconfs = numpy.loadtxt(self.name+'_nconf.txt',dtype=float)
        
        lp=[0]*len(self.stickers)
        
        hits=numpy.append(hits,lp)
        skips=numpy.append(skips,lp)
        predictions=numpy.append(predictions,lp)
        confs=numpy.append(confs,lp)
        nconfs=numpy.append(nconfs,lp)
        
        self.hits = [hits.tolist()]
        self.skips = [skips.tolist()]
        self.predictions = [predictions.tolist()]
        
        self.confidences = [confs.tolist()]
        self.negconfidences = [nconfs.tolist()]
        
        for p in self.predictorList:
            p.restore()
    
    
    def reset(self,since=None,until=None):
        
        self.preprocessed = False
        
        if since is not None and since in self.dataManager.datesList:
            since_idx = self.dataManager.datesList.index(since)
        else:
            since_idx = self.startOffset
        
        if until is not None and until in self.dataManager.datesList:
            until_idx = self.dataManager.datesList.index(until)
        else:
            until_idx = len(self.dataManager.datesList)
        
        for si in range(0,len(self.stickers)):
            for ti in range(since_idx,until_idx):
                self.skips[si][ti] = 0
                self.hits[si][ti] = 0
                self.predictions[si][ti] = 0
                self.udw[si][ti] = [1,1]
                self.confidences[si][ti] = 0
                self.negconfidences[si][ti] = 0
        
        
        if self.name[0:3] in Configuration.histlens.keys():
            self.maxhistlen = Configuration.histlens[self.name[0:3]]
        else:
            self.maxhistlen = Configuration.fushistlen
        
    
    def predict(self,sticker,timestamp,context):
        return (0,(0,0),0)
    
    
    def getHit(self,timestamp,sticker):
        
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        direction=''
        hit=''
        
        if self.skips[sticker_index][timestamp_index]>0:
            return ''
        
        if self.predictions[sticker_index][timestamp_index]>0:
            direction='Up'
        
        if self.predictions[sticker_index][timestamp_index]<0:
            direction='Down'
            
        if self.hits[sticker_index][timestamp_index]>0:
            hit='!'
        
        return direction+hit
    
    def getSkip(self,timestamp,sticker):
        
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        
        return self.skips[sticker_index][timestamp_index]
    
    def sticker(self):
        return self.stickers[0]
    
    def getPrediction(self,timestamp,sticker):  
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        return self.predictions[sticker_index][timestamp_index]
    
    def getUDW(self,timestamp,sticker,direction):  
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        tuple = self.udw[sticker_index][timestamp_index]
        
        return tuple[direction]
    
    def setUDW(self,timestamp,sticker,direction,u):  
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        try:
            self.udw[sticker_index][timestamp_index][direction] = u
        except:
            pass
    
    def getConfidence(self,timestamp,sticker):  
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        return self.confidences[sticker_index][timestamp_index]
    
    def getnegConfidence(self,timestamp,sticker):  
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        return self.negconfidences[sticker_index][timestamp_index]
    
    def recentPredictions(self,timestamp,sticker,depth=Configuration.metrhistlen):  
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        startindex = max(0,timestamp_index-depth)
        return self.predictions[sticker_index][startindex:timestamp_index]
    
    def concretePrediction(self,timestamp,sticker):
        return self.skips[sticker_index][timestamp_index]<=0 and self.predictions[sticker_index][timestamp_index]!=0
    
    def setPrediction(self,timestamp,sticker,prediction,confidence,skip):  
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        data = self.dataManager.getAt(sticker,'close',timestamp)
    
        self.predictions[sticker_index][timestamp_index] = int(numpy.sign(prediction))
        
        (p,n)=confidence
        
        self.confidences[sticker_index][timestamp_index] = p
        self.negconfidences[sticker_index][timestamp_index] = n
        
        if skip:

            self.skips[sticker_index][timestamp_index] = 1
        else: # not skip
            if prediction*data>0:
                self.hits[sticker_index][timestamp_index] = 1
    
    def invertPrediction(self,timestamp,sticker,inv):  
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        old_prediction=self.predictions[sticker_index][timestamp_index]
        self.predictions[sticker_index][timestamp_index] = inv*old_prediction
        
    
    def historyReputation(self,timestamp,sticker,depth=Configuration.metrhistlen,offset=-1):
        
        if offset<0:
            offset=self.startOffset
            
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp) # NOT INCLUDED
        if timestamp_index<=offset:
            return 0
        
        start_index = max(offset,timestamp_index-depth)
        depth = timestamp_index-start_index
        if depth<=0:
            return 0
        
        concrete_guesses_in_history = depth-sum(self.skips[sticker_index][timestamp_index-depth:timestamp_index])
        hits_in_history = sum(self.hits[sticker_index][timestamp_index-depth:timestamp_index])  
        if concrete_guesses_in_history==0:
            return 0
        return float(hits_in_history/concrete_guesses_in_history)
    
    def scores(self,timestamp,depth=Configuration.metrhistlen):
        sticker_index = self.stickers.index(self.sticker())
        timestamp_index = self.timestamps.index(timestamp)
        h = self.hits[sticker_index][timestamp_index-depth:timestamp_index]
        m = numpy.nanmean(h)
        if m==0.0:
            return 0
        sd = numpy.nanstd(h)
        return 1/sd
        
    def slops(self,timestamp,sticker):
        sticker_index = self.stickers.index(sticker)
        timestamp_index = self.timestamps.index(timestamp)
        
        return [e.slopes[sticker_index][timestamp_index] for e in self.estimators]
    
    def posSlopes(self,timestamp,sticker):
        z = self.slops(timestamp,sticker)
        return all([x>0 for x in z])
    
    
    def recentGains(self,timestamp,sticker,depth=Configuration.metrhistlen):
        
        hist=[]
        lastGain=0
        timestamp_index = self.timestamps.index(timestamp) # NOT INCLUDED
        start_index = max(self.startOffset, timestamp_index-depth)
        d = 0
    
        while timestamp_index>start_index:
            tstamp = self.timestamps[timestamp_index]
        
            hist.append(self.perfMetric(tstamp,sticker,depth))
    
            timestamp_index = timestamp_index - 1
            d = d + 1
        return hist

    
    def recentDailyGains(self,timestamp,sticker,depth=Configuration.metrhistlen):
        
        hist=[]
        timestamp_index = self.timestamps.index(timestamp)-1 # NOT INCLUDED
        start_index = timestamp_index-depth
        d = depth
        
        while d>0:
            tstamp = self.timestamps[timestamp_index]
            lg = self.dailyGain(tstamp,sticker)
            hist.append(lg)
            d = d-1
            timestamp_index = timestamp_index -1
        return hist
            
    def maxDD(self,timestamp,sticker):
        gains = self.recentGains(timestamp, sticker)
        ser = pandas.Series(gains)
        max2here = pandas.expanding_max(ser)
        dd2here = ser - max2here
        return math.fabs(dd2here.min())
    
    def sharpe(self,timestamp,sticker):
        gains = self.recentDailyGains(timestamp, sticker)
        m = numpy.mean(gains)
        v = numpy.std(gains)
        if v==0.0:
            return 0
        else:
            return m/v
    
    
    def dailyGain(self,timestamp,sticker):
        skip = self.getSkip(timestamp, sticker)
        if skip>0:
            return 0
        else:
            prediction = self.getPrediction(timestamp, sticker)
            delta = self.dataManager.getAt(sticker,'close',timestamp)
            return numpy.sign(prediction)*delta
        
    
    def perfMetric(self,timestamp,sticker,depth=Configuration.metrhistlen,offset=-1):
        if offset<0:
            offset=self.startOffset
            
        conf = self.getConfidence(timestamp, sticker)
        if Configuration.metricGain==True:
            metric = self.historyGain(timestamp,sticker,depth,offset)
        else:
            metric = self.historyReputation(timestamp,sticker,depth,offset)
        return metric
    
    def historyGain(self,timestamp,sticker,depth=Configuration.metrhistlen,offset=-1):
        if offset<0:
            offset=self.startOffset
            
        timestamp_index = self.timestamps.index(timestamp) # NOT INCLUDED
        if timestamp_index<=offset:
            return 0
        
        start_index = max(offset,timestamp_index-depth)
        depth = timestamp_index-start_index
        if depth<=0:
            return 0
        gain=0
        
        for ts in range(start_index,timestamp_index): # not includes timestamp_index
            tstamp = self.dataManager.datesList[ts]
            delta = self.dailyGain(tstamp,sticker)
            if math.isnan(delta) or math.isinf(delta):
                delta=0
            gain=gain+delta
        
        #scores=[self.dailyGain(self.timestamps[tsi],sticker) for tsi in range(start_index,timestamp_index)]
        
        return gain
        #return Tools.decaysum(scores)
    
    
    def skipRate(self,timestamp,sticker,depth):
        timestamp_index = self.timestamps.index(timestamp) # NOT INCLUDED
        if timestamp_index<self.startOffset:
            return 0
        
        start_index = max(self.startOffset,timestamp_index-depth)
        depth = timestamp_index-start_index+1
        if depth<=0:
            return 0
        
        score=0
        skips=0
        for tsi in range(start_index+1,timestamp_index):
            score=score+1
            
            if self.getSkip(self.timestamps[tsi],sticker)>0:
                skips=skips+1
                
        if skips==0:
            return 0
        else:
            return skips   
    
    def preprocess(self,since=None,until=None):
        #Tools.trace('')
        if 'sticker_' in self.name or 'neg(' in self.name:
            Tools.logm('\n Predictor {0} '.format(self.name))
        
        h=self.maxhistlen    
        ds = self.dataManager.getDataset()
        if self.preprocessed:
            return
        
        if since is not None and since in self.dataManager.datesList:
            id = self.dataManager.datesList.index(since)
        else:
            id = self.startOffset
            
        for sticker in self.stickers:
            starts = time.time()
            tsRange=self.dataManager.datesList[id:]
           
            for timestamp in tsRange:
                if until is not None and timestamp==until:
                    break
                closes=self.dataManager.getDataset().get(sticker,'close',timestamp,h)
                volumes = self.dataManager.getDataset().get(sticker,'volume',timestamp,h)
                highs = self.dataManager.getDataset().get(sticker,'high',timestamp,h)
                lows = self.dataManager.getDataset().get(sticker,'low',timestamp,h)
                opens = self.dataManager.getDataset().get(sticker,'open',timestamp,h)
                
                tindex = self.dataManager.datesList.index(timestamp)
                dates = self.dataManager.datesList[max(0,tindex-h):tindex]
                            
                try:     
                    (decision,confidence,skip)=self.predict(sticker,timestamp,[highs,lows,closes,volumes,opens,dates])
                    self.setPrediction(timestamp, sticker,decision,confidence,skip)
              
                except:
                    traceback.print_exc()
                    
                del closes
                del highs
                del lows
                del volumes
            del tsRange
           
        ends = time.time()
       
    
        self.preprocessed=True
        if 'sticker_' in self.name or 'neg(' in self.name:
            Tools.logm('... finished ')
        
            
                                
            
        
       

        