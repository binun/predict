from predictors import Predictor
import numpy
from numpy import fft

class curvePredictor(Predictor.Predictor):
    
    def __init__(self, dataManager,alg): 
        super().__init__(alg,dataManager)
    
    def fourierExtrapolation(self,x):
        n = x.size
        n_predict = 10
        n_harm = 10                  
        t = numpy.arange(0, n)
        p = numpy.polyfit(t, x, 1)         
        x_notrend = x - p[0] * t        
        x_freqdom = fft.fft(x_notrend)  
        f = fft.fftfreq(n)            
        indexes = list(range(n))
  
        indexes.sort(key = lambda i: numpy.absolute(f[i]))
 
        t = numpy.arange(0, n + n_predict)
        restored_sig = numpy.zeros(t.size)
        for i in indexes[:1 + n_harm * 2]:
            ampli = numpy.absolute(x_freqdom[i]) / n   
            phase = numpy.angle(x_freqdom[i])          
            restored_sig += ampli * numpy.cos(2 * numpy.pi * f[i] * t + phase)
            return restored_sig + p[0] * t
    
    def predict(self,sticker,timestamp,context):
        closehist = context[:,2]
        args = list(range(0,len(closehist)))
        vals=closehist
        d = self.calculateNext(args, self.name,vals)
        return (int(numpy.sign(d - closehist[-1])),1,False)
    
    def calculateNext(self,kind,args,vals):
        if kind=='poly':
            z = numpy.polyfit(args, vals, 3)
            p = numpy.poly1d(z)
            d = p(len(vals))
            return d
        if kind=='fourier':
            extrapolation = self.fourierExtrapolation(vals, self.advance)
            d = extrapolation[-1]
            return d
        