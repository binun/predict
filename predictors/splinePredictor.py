from predictors import Predictor
import numpy
from Utils import Utils
from scipy import interpolate
from Configuration import Configuration

class splinePredictor(Predictor.Predictor):
   
    def __init__(self, dataManager,hist=-1):
        super().__init__("spline",dataManager,hist)
    
    def predict(self,sticker,timestamp,context):
        
        closehist = context[2]
        volumehist = context[3]
        maxv = numpy.max(volumehist)
        
        l = len(closehist)
        
        X=numpy.zeros(l)
        Y=numpy.zeros(l)
        Z=numpy.zeros(l)
        
        for i in range(0,l):        
            Z[i] = Utils.cancelNan(numpy.sign(closehist[i+1]-closehist[i]))
            
            Y[i] = Utils.cancelNan(closehist[i])
            X[i] = Utils.cancelNan(volumehist[i]/maxv)

        
        f = interpolate.interp2d(X, Y, Z, kind='quintic')
        Xend = Utils.cancelNan(volumehist[l]/maxv)
        Yend = Utils.cancelNan(closehist[l])
        d = f(Xend, Yend)
        
        decision=0
        tomorrow = d
        today = closehist[-1]
        yesterday = closehist[-2]
        
        if (tomorrow-today)/today > Configuration.minclosegap and tomorrow-today>today-yesterday:
            decision=1
            
        if (tomorrow-today)/today < -Configuration.minclosegap and tomorrow-today<today-yesterday:
            decision=-1
        
        return decision
        
        return d
        
        
        