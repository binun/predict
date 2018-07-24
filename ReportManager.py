# http://www.turingfinance.com/computational-investing-with-python-week-one/
import os
import gc
import traceback
from Service.Utilities import Tools
from Configuration import Configuration
import datetime
import numpy
import time
from itertools import chain
import pandas
from pandas.tseries.offsets import BDay
#import matplotlib.pyplot as plt

class ReportManager(object):


    def __init__(self, fusion):
        
        self.engine = fusion
        self.engine.setReportMan(self)
        
        self.now=time.strftime(Configuration.timestamp_format)
        self.dir="output_{0}_{1}".format(self.engine.dataManager.datasource,str(self.now))
        if len(Configuration.prefix)>0:
            self.dir = self.dir+'__'+Configuration.prefix
        
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        
        self.fusionCalculated=[]
        self.predictors = fusion.predictorList
        
        self.log = os.path.join(self.dir, "aggregation.csv")
        self.pict=os.path.join(self.dir, "fusion.png")
        self.predlog = Configuration.predfile
        self.actlog = "maillog.csv"
        
        self.startOffset = self.engine.startOffset           
        self.lastMessage = ''
    

    def updateMaillog(self):
        model = self.engine.dataManager
        df=None
        try:
            df = pandas.read_csv("maillog.csv",header=None)
        except:
            return
        hist = df.values

        f = open(self.actlog,'wt')
        for histitem in hist:
            td = pandas.Timestamp(histitem[0])
            tds = td.strftime("%Y-%m-%d")
            predictions = str(histitem[2]).replace(':',' ').split(' ')
            li = predictions.index("Longs")
            si = predictions.index("Shorts")
            sum=0
            count=0
            for i in range(li+1,si):
                sticker = predictions[i]
                try:
                    sum = sum+model.getAt(sticker,'close',tds)
                    count=count+1
                except:
                    continue
    
            for i in range(si+1,len(predictions)):
                sticker = predictions[i]
                try:
                    sum = sum-model.getAt(sticker,'close',tds)
                    count=count+1
                except:
                    continue
    
            av = 0
            if count>0:
                av= sum/count
            f.write('{0},{1},{2}\n'.format(tds,str(av),histitem[2]))
        f.close()
    
    def reportDetail(self,detpath,sticker,pred):

        if 'neg' in pred.name:
            return
        print('Detalizing {0}'.format(pred.name))
        
        log = os.path.join(detpath, "{0}.csv".format(pred.name))
        indSuccCaptions = ['Success_'+s.name for s in filter(lambda pred: 'neg' not in pred.name,pred.predictorList)]
        header='{0},{1},{2},{3},{4},{5},{6},{7}\n'.format('date','dateNo','fusSuccessRate','fusHit','fusGain','dailyGain','deltaClose',','.join(indSuccCaptions))
        
        tstamps = self.engine.dataManager.datesList[self.startOffset:]
        messages={1:'Up',-1:'Down',0:'Zero'}
    
        with open(log, 'w') as f:
            f.write(header)
            for tindex,timestamp in enumerate(tstamps):
    
                datestr = timestamp.replace("-","_")
                dateno = str(self.engine.dataManager.datesList.index(timestamp))
                fusionSuccess = str(pred.historyReputation(timestamp,sticker))
                
                fusionGain = str(pred.historyGain(timestamp,sticker,10000,self.startOffset))
                
                fusionDelta = str(pred.dailyGain(timestamp,sticker))
                
                rawDelta = str(self.engine.dataManager.getAt(sticker, 'close', timestamp))
                
                fusionHit = str(pred.getHit(timestamp,sticker))
                fp=pred.getPrediction(timestamp,sticker)
                indsuccesses = [p.historyReputation(timestamp,p.sticker(),p.maxhistlen) for p in filter(lambda pred: 'neg' not in pred.name,pred.predictorList)]
                succStr = ",".join(map(str, indsuccesses))
                    
                message='{0},{1},{2},{3},{4},{5},{6},{7}\n'.format(datestr,dateno,fusionSuccess,fusionHit,fusionGain,fusionDelta,rawDelta,succStr)
                f.write(message)
            f.close()
        
        del tstamps
        del messages
        gc.collect()
                
    
    def reportDetails(self):
        detpath = os.path.join(self.dir,"details")
         
#         if not os.path.exists(detpath):
#             os.makedirs(detpath)
            
            
        #for pred in self.predictors:
                      
            #sticker = pred.stickers[0]
#             try:
#                 self.reportDetail(detpath,sticker,pred)
#             except:
#                 traceback.print_exc()
    
    def reportAggregation(self,since=None,until=None):
        
        log=self.log
        tstamps = self.engine.dataManager.datesList
        if since is None:
            s = self.startOffset
        else:
            s = tstamps.index(since)
        
        if until is None:
            u = len(tstamps)
        else:
            u = tstamps.index(until)
            mon = until.split('-')[1]
            log=os.path.join(self.dir, mon+"_aggregation.csv")
            
        
        
        print('Aggregation started')
        tstamps = tstamps[s:u]
        predGainCaptions = ['G_'+s.name for s in self.predictors]
        predSuccCaptions = ['SR_'+s.name for s in self.predictors]
        predConfCaptions = ['C_'+s.name for s in self.predictors]
        predCloseCaptions = ['R_'+s.name for s in self.predictors]
        
        captions = list(chain.from_iterable(zip(predGainCaptions,predSuccCaptions,predConfCaptions,predCloseCaptions)))
         
        aheader='{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n'.format('date','dateno','rawGain','accumFusionGain','fusionDeltaGain','selSuccess','deltaStatistics','bestStickers','detailDistr','bestGainDistr',','.join(captions))
        
        fusgains={}
        drs={}
        
        posdeltas=0
        negdeltas=0
        with open(log, 'wt') as f:
            
            f.write(aheader)
            stillzeros=True
            for tindex,timestamp in enumerate(tstamps):
                
                fusgain = self.engine.historyGain(timestamp)
                dr = self.engine.dataManager.dailyAccumulatedRaw(timestamp,self.startOffset,self.engine.skips)
                dateno = str(self.engine.dataManager.datesList.index(timestamp))
                
                srSuccess=''
                if self.engine.skips[timestamp]==False:
                    srSuccess = str(self.engine.estimatedSuccessRates[timestamp])
                    
                bests=None
                try:     
                    bests = self.engine.bestStickers(timestamp)
                except:
                    bests=[]
                
                longs=[]
                shorts=[]
                
                fusgains[timestamp]=fusgain
                drs[timestamp]= dr
                 
                for (sticker,prediction) in bests:
                    
                    if prediction>0:
                        longs.append(sticker)
                    if prediction<0:
                        shorts.append(sticker)
             
                bestStickersMessage=''
                if self.engine.skips[timestamp]==False:
                    bestStickersMessage='Longs:{0}  Shorts:{1}'.format('_'.join(longs), '_'.join(shorts))
                    self.lastMessage = 'Longs:{0} Shorts:{1}'.format(' '.join(longs), ' '.join(shorts))
                
                
                indgains=[pred.historyGain(timestamp,pred.sticker(),10000,self.startOffset) for pred in self.predictors]   
                gainStr=",".join(map(str, indgains))
                
                indsuccesses = [pred.historyReputation(timestamp,pred.sticker(),Configuration.metrhistlen) for pred in self.predictors]
                succStr = ",".join(map(str, indsuccesses))
                
                indconfidences = [pred.getConfidence(timestamp,pred.sticker()) for pred in self.predictors]
                confStr = ",".join(map(str, indconfidences))
                
                indcloses = [pred.dataManager.getAt(pred.sticker(),'close',timestamp) for pred in self.predictors]
                closeStr = ",".join(map(str, indcloses))
                
                metrics = list(chain.from_iterable(zip(indgains, indsuccesses, indconfidences,indcloses)))
                metrStr = ",".join(map(str, metrics))
                
                delta=''
                deltastat=''
                dist= ''
                detdist = ''
                dailyFusionGain=''
                
                if self.engine.skips[timestamp]==False:
                    delta = self.engine.deltagain[timestamp]
                
                    dailyFusionGain = str(delta)
                    if delta>0:
                        posdeltas=posdeltas+1
                    if delta<0:
                        negdeltas=negdeltas+1
                    deltastat='Pos:{0}-Neg:{1}'.format(str(posdeltas),str(negdeltas))
                    dist = self.engine.distr[timestamp]
                    detdist = self.engine.detaildistr[timestamp]
                
                message = '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n'.format(timestamp.replace("-","_"),dateno,str(dr),str(fusgain),dailyFusionGain,srSuccess,deltastat,bestStickersMessage,dist,detdist,metrStr)
                f.write(message)
                
                del longs
                del shorts
            
            f.close()
            
            print('Aggregation saved')
            
            
        del fusgains
        del tstamps
        if Configuration.online==True:
            with open(self.actlog, 'a') as fa:
                td = pandas.Timestamp(datetime.datetime.now())+BDay(1)
            
                addt='{0},{1},{2}\n'.format(td.strftime("%b-%d-%Y"),'0',self.lastMessage)
                fa.write(addt)
                fa.close()
        
            self.updateMaillog()
            