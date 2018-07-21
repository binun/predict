
import numpy
import os
from Service.Utilities import Tools
from Configuration import Configuration
from predictors.bernoulliPredictor import bernoulliPredictor
from predictors.armaPredictor import armaPredictor
from predictors.dlPredictor import dlPredictor
from predictors.fusionPredictor import fusionPredictor
from heapq import nlargest
import re

from sklearn.tree import DecisionTreeClassifier

from sklearn.neighbors import KNeighborsClassifier


from predictors.featurePredictor import featurePredictor
from predictors.polyPredictor import polyPredictor
from predictors.lzwPredictor import lzwPredictor
from predictors.sequencePredictor import sequencePredictor
from predictors.forexsimPredictor import forexsimPredictor
from predictors.markovPredictor import markovPredictor
from sklearn.naive_bayes import MultinomialNB,GaussianNB
from sklearn.linear_model.logistic import LogisticRegression

from sklearn.svm import SVC,SVR
from scipy import stats
from numpy import arange,array,ones
from numpy import median
import gc
import time


# linear_model.SGDRegressor(),
# linear_model.BayesianRidge(),
# linear_model.LassoLars(),
# linear_model.ARDRegression(),
# linear_model.PassiveAggressiveRegressor(),
# linear_model.TheilSenRegressor(),

class sticker_fusionPredictor(fusionPredictor):
  
    def __init__(self,dataManager,stick,fusMethod,context=None):
        
        self.predictorList=[]
        self.stickers = [stick]
        
        name='sticker_{0}'.format(stick)
        super().__init__(name,dataManager,self.predictorList,[stick],fusMethod)
        
        
        self.fushistlen = Configuration.fushistlen
        self.startOffset = self.histlen
        
        if Configuration.dry==False:
            self.basicPredsGenerate()
        
        self.maxhistlen = max([p.maxhistlen for p in self.predictorList])
    
    def reset(self,since=None,until=None):
        for p in self.predictorList:
            p.reset(since,until)
        super().reset(since,until)
        

    
    def basicPredsGenerate(self):
        if len(self.predictorList)>0:
            return
        
        #self.predictorList.append(markovPredictor(self.dataManager,-1,context=self))
        for i in range(1,sequencePredictor.maxlen+1):
            self.predictorList.append(sequencePredictor(self.dataManager,-1,context=self,fixlen=i))
        
        #self.predictorList.append(lzwPredictor(self.dataManager,-1,context=self,way='lzma'))
#         self.predictorList.append(lzwPredictor(self.dataManager,-1,context=self,way='zlib'))
#         self.predictorList.append(lzwPredictor(self.dataManager,-1,context=self,way='gzip'))
        #self.predictorList.append(lzwPredictor(self.dataManager,-1,context=self,way='huff'))
        #self.predictorList.append(sequencePredictor(self.dataManager,-1,context=self))
        
        #self.predictorList.append(prophetPredictor(self.dataManager,-1,context=self))
        #self.predictorList.append(armaPredictor(self.dataManager,-1,context=self))
        
#         dt=RandomForestClassifier(n_estimators=10,random_state=1)
#         kn = KNeighborsClassifier(n_neighbors=20,weights='distance')
#         svm = SVC(kernel='rbf',random_state=0,probability=True)
#         lr = LogisticRegression()
#         lda = LinearDiscriminantAnalysis(solver="svd", store_covariance=True)
        
        #svr = SVC(kernel='rbf',random_state=0,probability=True)
        
        #gboost = GradientBoostingClassifier(n_estimators=10, random_state=0)
        #scipy_sensors = [(lr,'l'),(dt,'d'),(kn,'k'),(svp,'pl'),(svr,'rb'),(gboost,'g'),(bs,'bs')]
#         scipy_sensors = [(lr,'l'),(dt,'d'),(kn,'k'),(svm,'sv')]   
#         scipypreds = [featurePredictor(self.dataManager,bgsname,bgs,-1,context=self) for (bgs,bgsname) in scipy_sensors]  
#         del scipy_sensors
#         
#         #self.predictorList.extend(scipypreds)
# 
#         #self.predictorList.append(dlPredictor(self.dataManager,-1,context=self))
#         self.predictorList.append(sequencePredictor(self.dataManager,-1,context=self))
#         #self.predictorList.append(polyPredictor(self.dataManager,-1,context=self))
# 
#         #self.predictorList.append(armaPredictor(self.dataManager,-1,context=self))

        
        
        for p in self.predictorList:
            p.stickers=self.stickers
        

    def predict(self,sticker,timestamp,context):
    
        if Configuration.dry:  
            (decision,confidence,skip)=(1,1,False)
        else:
            (decision,confidence,skip)=super().predict(sticker,timestamp,context)
               
        return (decision,confidence,skip)
    
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

    
        
            
        
        
        
        