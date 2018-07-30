
import os
import gc
import numpy
from Service.Utilities import Tools
from Configuration import Configuration
from functools import cmp_to_key
from heapq import nlargest
from predictors.sticker_fusionPredictor import sticker_fusionPredictor
from predictors.negationPredictor import negationPredictor
import math
from itertools import product
from numpy import median
import operator
import pandas
import traceback
from pandas.io.parsers import read_csv


class Fuser(object):
    
    def __init__(self,dataManager):
        
        
        self.bestPredictors={}
        self.predictorList = []
        self.dataManager = dataManager
        self.stickers = []
        
        self.beststickers={}
        self.skips={}
        self.distr={}
        self.detaildistr={}
        self.deltagain={}
        self.predDict={}
        self.metrlen = Configuration.metrhistlen
        self.estimatedSuccessRates={}
        self.invert=1
        self.metric=[]
        self.currentMetric=[]
        self.repman = None
        self.reportPoint=None
        
        for st in dataManager.stickers:
            sp = sticker_fusionPredictor(dataManager,st,context=None,fusMethod=Configuration.deffustype)
            self.predictorList.append(sp)
            self.predDict[sp.name] = sp
            
            
            sp1 = negationPredictor(sp)
            self.predictorList.append(sp1)
            self.predDict[sp1.name] = sp1
           
            self.stickers.append(st)
            
        self.startOffset = Configuration.seloffset
        self.predOffset = max([p.startOffset for p in self.predictorList])

        self.estimatedSuccessRates[dataManager.datesList[self.startOffset]] = 0
        self.log=dataManager.datasource+'_optimal.txt'
        self.logI=dataManager.datasource+'_optconfigs.txt'
        self.f=None
    
    def setReportMan(self,rm):
        self.repman=rm
        
    def reset(self,since=None,until=None):
        for p in self.predictorList:
            p.reset(since,until)
        
        if since is not None and since in self.dataManager.datesList:
            since_idx = self.dataManager.datesList.index(since)
        else:
            since_idx = Configuration.seloffset
        
        if until is not None and until in self.dataManager.datesList:
            until_idx = self.dataManager.datesList.index(until)
        else:
            until_idx = len(self.dataManager.datesList)
        
        rng=range(since_idx,until_idx)
        cleartimes=self.dataManager.datesList[since_idx:until_idx]
        
        for ts in cleartimes:
            self.bestPredictors[ts] = []
            self.distr[ts]=''
            self.detaildistr[ts]=''
            self.deltagain[ts] = 0   
            self.estimatedSuccessRates[ts] = 0
            self.skips[ts] = False
            
        gc.collect()
        
    def runseq(self,ndays=5):
        
        datas = self.dataManager.datesList[Configuration.seloffset:]
        
        splitpoints=[None]
        periods=int(len(datas)/ndays)
        
        for i in range(1,periods-1):
            splitpoints.append(datas[i*ndays])
        splitpoints.append(None)
        
        for i in range(0,len(splitpoints)-1):
            today = splitpoints[i]
            tomorrow = splitpoints[i+1]
            self.trainRun(today,tomorrow)
            
        #if Configuration.online==True:
            #self.save()
            
        
    
    def testRun(self,since=None,until=None):
        self.reset(since,until)
        self.runAll(since,until)
    
    def trainRun(self,since=None,until=None):
            
        seqhists = [70,80]
        fushists=[10,15,20,25]
        minprobs = [0.6] 
        selhists=[15]
        bestcounts_l=[0.0,0.05,0.1,0.15,0.2]
        bestcounts_s=[0.0,0.05,0.1,0.15,0.2]
    
#         seqhists = [80]
#         fushists=[10]
#         minprobs = [0.6] 
#         selhists=[15]
#         bestcounts_l=[0.1]
#         bestcounts_s=[0.1]
        
        optconfig=[Configuration.goodStickerProb,Configuration.metrhistlen,Configuration.fushistlen,80,Configuration.bestCountL,Configuration.bestCountS]
        self.metric.clear()
        Configuration.train=True    
        for seqhist,fushist,minprob,selhist,bestcountl,bestcounts in product(seqhists,fushists,minprobs,selhists,bestcounts_l,bestcounts_s):
            
            if bestcountl+bestcounts==0 and len(bestcounts_l)>1 and len(bestcounts_s)>1:
                continue
            
            msg=' '.join(map(str,[minprob,selhist,fushist,seqhist,bestcountl,bestcounts]))
            print(msg,end=' ')
            
            Configuration.goodStickerProb = minprob
            Configuration.metrhistlen = selhist
            Configuration.fushistlen = fushist
            Configuration.histlens["seq"] = seqhist
            Configuration.bestCountL = bestcountl
            Configuration.bestCountS = bestcounts
            
            self.reset(since,until)
            self.runAll(since,until)
            (past,cur,prob)=self.increased()
            if prob:
                
                optconfig=[minprob,selhist,fushist,seqhist,bestcountl,bestcounts]
                self.metric=self.currentMetric.copy()
                print(' ... improved from {0} to {1}\n'.format(str(past),str(cur)))
                
                f1=open(self.logI,'at')
                f1.write(msg+'\n')
                f1.close()
                
            else:
                print(' ')
                
        
        Configuration.train=False
        
        Configuration.goodStickerProb = optconfig[0]
        Configuration.metrhistlen = optconfig[1]
        Configuration.fushistlen = optconfig[2]
        Configuration.histlens["seq"] = optconfig[3]
        Configuration.bestCountL=optconfig[4]
        Configuration.bestCountS = optconfig[5]
        
        msg=','.join(map(str,optconfig))
        print(msg)
        
        self.f=open(self.log,'wt')
        self.f.write(msg+'\n')
        self.f.close()
        
        self.reset(since,until)
        self.runAll(since,until)
    
                   
    def increased(self):
        if len(self.metric)==0 or len(self.currentMetric)==0:
            return (0,0,True)
        
        t=min(10,min(len(self.currentMetric),len(self.metric)))
        p=numpy.mean(self.metric[-t:])
        c=numpy.mean(self.currentMetric[-t:])
        
        return (p,c,c>p)

        
    def buildPredictions(self,since=None,until=None):
        
        self.currentMetric.clear()
        if since is not None and since in self.dataManager.datesList:
            id = self.dataManager.datesList.index(since)
        else:
            id = Configuration.seloffset
            
        if Configuration.bestCountL+Configuration.bestCountS==0:
            bsc = int(0.1*len(self.stickers))
        else:
            bsc = int((Configuration.bestCountL+Configuration.bestCountS)*len(self.stickers))
        tstamps = self.dataManager.datesList[id:]
        for tindex,timestamp in enumerate(tstamps):
            
            if until is not None and timestamp==until:
                break
         
            self.bestPredictors[timestamp] = []
            self.distr[timestamp]=''
            self.detaildistr[timestamp]=''
            self.deltagain[timestamp] = 0   
            self.estimatedSuccessRates[timestamp] = 0
            self.skips[timestamp] = False
            
            goodList = self.predictorList
            if len(goodList)>=4:       
                goodList = list(filter(lambda pred: pred.getSkip(timestamp,pred.sticker())<=0, goodList))
                if timestamp!=tstamps[-1]:
                    goodList = list(filter(lambda pred: self.dataManager.stickerActive(pred.sticker(),timestamp), goodList))   
                goodList = list(filter(lambda pred: pred.getPrediction(timestamp,pred.sticker())!=0, goodList))
                goodList = list(filter(lambda pred: pred.historyReputation(timestamp,pred.sticker())>=Configuration.goodStickerProb,goodList))
                #goodList = list(filter(lambda pred: pred.historyGain(timestamp,pred.sticker(),depth=50,offset=self.startOffset)>0,goodList))
            
                if len(goodList)<2:
                    continue
                goodList = sorted(goodList,key=lambda p:p.historyGain(timestamp,p.sticker(),depth=50))
                goodList = goodList[-2*bsc:]        
                
                goodList = sorted(goodList,key=lambda p:p.getConfidence(timestamp,p.sticker()))
                goodList = goodList[-bsc:]
            
            goodList_f=[]
            filtered_stickers=[]
            for p in goodList[::-1]:
                actor=p
                if 'neg' in p.name:
                    actor=p.predictor_
                if actor.getSkip(timestamp,actor.sticker())<=0 and actor.sticker() not in filtered_stickers:
                    goodList_f.append(actor)
                    filtered_stickers.append(actor.sticker())
                    
            
            if Configuration.bestCountL+Configuration.bestCountS>0:
                wanted_long=int(Configuration.bestCountL*len(goodList_f))
                wanted_short = int(Configuration.bestCountS*len(goodList_f))
            
                goodLong = list(filter(lambda pred: pred.getPrediction(timestamp,pred.sticker())>0, goodList_f))
                goodShort = list(filter(lambda pred: pred.getPrediction(timestamp,pred.sticker())<0, goodList_f))
                 
                goodLong = sorted(goodLong,key=lambda p:p.historyGain(timestamp,p.sticker(),depth=7))
                goodShort = sorted(goodShort,key=lambda p:p.historyGain(timestamp,p.sticker(),depth=7))
                 
                L=goodLong[-wanted_long:]
                S=goodShort[-wanted_short:]
                goodList_f.clear()
                goodList_f.extend(L)
                goodList_f.extend(S)
                
                del goodLong
                del goodShort
                del L
                del S
            
            self.bestPredictors[timestamp] = goodList_f
            
            if timestamp!=tstamps[-1]:
                gainMessages={}
                pos = 0
                av=0
                for p in goodList_f:
                    pn = p.name
                    g = p.dailyGain(timestamp,p.sticker())
                    gainMessages[pn] = g
                    if g>0:
                        pos=pos+1
                    av=av+g
              
                gainMsgSorted = sorted(gainMessages.items(), key=operator.itemgetter(1))
              
                ds1 = ['{0}-G:{1} SR:{2}'.format(p.name,str(p.historyGain(timestamp,p.sticker(),depth=100,offset=self.startOffset)),str(p.historyReputation(timestamp,p.sticker()))) for p in goodList_f]
                ds = [str(format(y, '.2f')) for (x,y) in gainMsgSorted]
                (cpno,cpday) = Tools.weekday(timestamp)
                Tools.logm(cpday + ' ' + timestamp + ' : ' + str(float(pos/len(goodList_f))))
                
                es = float(pos/len(goodList_f))
                self.estimatedSuccessRates[timestamp] = es
                self.currentMetric.append(es)
                
                self.distr[timestamp] = ' '.join(ds)
                self.detaildistr[timestamp] = ' '.join(ds1) 
                self.deltagain[timestamp] = av/len(goodList_f)
                
                if Configuration.train==False and Configuration.online==False and self.dataManager.switchedMonth(timestamp):
                    
                    print(timestamp + ' REPORT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    self.repman.reportAggregation(self.reportPoint,timestamp)
                    self.reportPoint = timestamp
                
                del gainMsgSorted
                del gainMessages
                
            del goodList_f     
            del goodList
             
        
    def runAll(self,since=None,until=None):
          
        for pred in self.predictorList:          
            pred.runAll(since,until)
        
        self.buildPredictions(since,until)
        
            
    
    def bestStickers(self,timestamp=None):
        if timestamp is None:
            timestamp=self.dataManager.datesList[-1]
            
        if timestamp not in self.bestPredictors.keys():
            return []
        bs=[]
        p=[]
        n=[]
        
        for bp in self.bestPredictors[timestamp]:
            sticker=bp.sticker()
            nm = bp.name
            prediction = bp.getPrediction(timestamp,sticker)
            skip = bp.getSkip(timestamp,sticker)
            if skip:
                continue
            
            if 'neg' in nm:
                pred=-int(numpy.sign(prediction))
            else:
                pred=int(numpy.sign(prediction))
            
            if pred>0 and sticker not in p:
                bs.append((sticker,1))
                p.append(sticker)
            
            if pred<0 and sticker not in n:
                bs.append((sticker,-1))
                n.append(sticker)
            
        return bs
        
    def historyReputation(self,timestamp,depth=1000): 
        timestamp_index = self.dataManager.datesList.index(timestamp)
        if timestamp_index<=self.startOffset:
            return 0
        
        start_index = max(self.startOffset,timestamp_index-depth)
        depth = timestamp_index-start_index
        if depth<=0:
            return 0
        
        gain=0
        skips=0
        for ts in range(timestamp_index-depth,timestamp_index): # not includes timestamp_index
            tstamp = self.dataManager.datesList[ts]
            if self.skips[tstamp]:
                skips=skips+1
                continue
            #delta = self.deltagain[tstamp]
            delta=self.estimatedSuccessRates[tstamp]
            
            if math.isnan(delta) or math.isinf(delta):
                delta=0
            
            gain=gain+delta
        if depth>skips:    
            return float(gain/(depth-skips))
        else:
            return 1.0
    
    def historyGain(self,timestamp,depth=1000): 
        timestamp_index = self.dataManager.datesList.index(timestamp)
        if timestamp_index<=self.startOffset:
            return 0
        
        start_index = max(self.startOffset,timestamp_index-depth)
        depth = timestamp_index-start_index
        if depth<=0:
            return 0
        
        gain=0
        
        for ts in range(start_index,timestamp_index): # not includes timestamp_index
            tstamp = self.dataManager.datesList[ts]
            delta = self.deltagain[tstamp]
            if math.isnan(delta) or math.isinf(delta) or self.skips[tstamp]:
                delta=0
            gain=gain+delta
            
        return gain
    
    def perfMetric(self,timestamp,depth=1000):
        if Configuration.metricGain:
            return self.historyGain(timestamp, depth)
        else:
            return self.historyReputation(timestamp, depth)
    
    def badPerformance(self,timestamp,depth=5):
        if Configuration.metricGain:
            return self.historyGain(timestamp, depth)<0
        else:
            return self.historyReputation(timestamp, depth)<=0.4
