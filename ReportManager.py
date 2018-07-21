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
        
        self.now=time.strftime(Configuration.timestamp_format)
        self.dir="output_{0}_{1}".format(self.engine.dataManager.datasource,str(self.now))
        if len(Configuration.prefix)>0:
            self.dir = self.dir+'__'+Configuration.prefix
        
        self.fusionCalculated=[]
        self.predictors = fusion.predictorList
        
        self.log = os.path.join(self.dir, "aggregation.csv")
        self.pict=os.path.join(self.dir, "fusion.png")
        self.predlog = Configuration.predfile
        self.actlog = "maillog.csv"
        
        self.startOffset = self.engine.startOffset           
        self.lastMessage = ''
    

    
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
         
        if not os.path.exists(detpath):
            os.makedirs(detpath)
            
            
        for pred in self.predictors:
                      
            sticker = pred.stickers[0]
#             try:
#                 self.reportDetail(detpath,sticker,pred)
#             except:
#                 traceback.print_exc()
    
    def reportAggregation(self):
        
        print('Aggregation started')
        
        tstamps = self.engine.dataManager.datesList[self.startOffset:]
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
        with open(self.log, 'w') as f:
            
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
        
        with open(self.actlog, 'a') as fa:
            td = pandas.Timestamp(datetime.datetime.now())+BDay(1)
            
            addt='{0},{1}\n'.format(td.strftime("%b-%d-%Y"),self.lastMessage)
            fa.write(addt)
            fa.close()
            
            
#         with open(self.predlog, 'w') as fp:
#             ls = ' '.join(longs)+"\n"
#             ss = ' '.join(shorts)+"\n"
#             fp.write(ls)
#             fp.write(ss)
#             fp.close()
#             
#         if Configuration.twsactive:
#             longs_with_vals=[]
#             shorts_with_vals=[]
#             
#             for l in longs:
#                 v = str(self.engine.dataManager.getDataset().getAt(l,'close',None))
#                 longs_with_vals.append('{0}:{1}'.format(l,v))
#         
#             for s in shorts:
#                 v = str(self.engine.dataManager.getDataset().getAt(s,'close',None))
#                 shorts_with_vals.append('{0}:{1}'.format(s,v))
#             
#             increment=0
#             fr = open(self.actlog,'r')
#             plines = fr.readlines()
#             fr.close()
#             pp = plines[-1].split(',')
#           
#             prev_longs = pp[1].split('_')
#             prev_shorts = pp[2].split('_')
#             for pl in prev_longs:
#                 [sticker,prev_close] = pl.split(':')
#                 now_close = self.engine.dataManager.getDataset().getAt(sticker,'close',None)
#                 increment = increment + (now_close-float(prev_close))/float(prev_close)
#                 
#             for ps in prev_shorts:
#                 [sticker,prev_close] = ps.split(':')
#                 now_close = self.engine.dataManager.getDataset().getAt(sticker,'close',None)
#                 increment = increment - (now_close-float(prev_close))/float(prev_close)
#             increment = increment / (len(prev_longs)+len(prev_shorts))
#         
#             with open(self.actlog, 'a') as fa:
#                 td = datetime.datetime.now()
#                 addt='{0},{1},{2},{3}\n'.format(td.strftime("%b-%d-%Y"),'_'.join(longs_with_vals),'_'.join(shorts_with_vals),str(increment))
#                 fa.write(addt)
#                 fa.close()
#         
#             os.system('java -jar mailer.jar {0}'.format(self.predlog))
        
            
        
        