from predictors import Predictor
import numpy
from numpy import fft

class surfacePredictor(Predictor.Predictor):
    
    def __init__(self, dataManager): 
        super().__init__("kk",dataManager)
        
    def predict(self,sticker,timestamp,context):
        
        highhist = context[0]
        lowhist = context[1]
        closehist = context[2]
        volumehist = context[3]
        amplhist = numpy.subtract(highhist,lowhist)
        
        h = len(closehist)
        x = numpy.zeros(h-1)
        y = numpy.zeros(h-1)
        z = numpy.zeros(h-1)
        
        query=[]
        query.append(100*(volumehist[-1]-volumehist[-2])/volumehist[-2])
        query.append(100*(amplhist[-1]-amplhist[-2])/amplhist[-2])
          
        
        for i in range(1,h-1): # h-1 is the last
            x[i] = 100*(volumehist[i]-volumehist[i-1])/volumehist[i-1]
            y[i] = 100*(amplhist[i]-amplhist[i-1])/amplhist[i-1]
            z[i] = 100*(closehist[i+1]-closehist[i])/closehist[i]
       
        args = list(range(0,h))
        d = self.calculateNext(args, self.name,x,y,z)
        return d
    
    def calculateNext(self,kind,x,y,z):
        if kind=='poly':
            return 0
        