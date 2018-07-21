
import numpy

from predictors.fusionPredictor import fusionPredictor
from Configuration import Configuration
from Service.Utilities import Tools
from math import fabs
import traceback
import gc

class sensorPredictor(fusionPredictor):
  
    def __init__(self,dataManager,preds,stickers,fusMethod,context=None):
        
        name = '['+'_'.join([p.name for p in preds])+']'
        
        super().__init__(name,dataManager,preds,stickers,fusMethod)
        
        nondup_preds = []
        nondup_names = []
        for p in preds:
            if stickers[0]!='dummy':
                p.stickers = stickers
            if p.name not in nondup_names:
                nondup_preds.append(p)
                nondup_names.append(p.name)
                
        del nondup_names
        
        self.stickers = stickers
        
        self.predictorList=nondup_preds
        
        self.histlen = max([p.histlen for p in self.predictorList])
        self.fushistlen = Configuration.fushistlen
        self.startOffset = self.histlen
    
    def averageGain(self,timestamp,depth):
        return numpy.mean([self.historyGain(timestamp,s,depth) for s in self.stickers])
    
    def averageReputation(self,timestamp,depth):
        return numpy.mean([self.historyReputation(timestamp,s,depth) for s in self.stickers])
    