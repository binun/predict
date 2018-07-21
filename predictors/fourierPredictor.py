from predictors import Predictor
import numpy as np
import pylab as pl
from numpy import fft
# https://gist.github.com/tartakynov/83f3cd8f44208a1856ce 
class fourierPredictor(Predictor.Predictor):
    
    def __init__(self, dataManager):
        super().__init__("fft",dataManager)
        self.nharm=10
        self.advance=1
        
    def fourierExtrapolation(self,x):
        n = x.size
        n_predict = 10
        n_harm = 10                  
        t = np.arange(0, n)
        p = np.polyfit(t, x, 1)         
        x_notrend = x - p[0] * t        
        x_freqdom = fft.fft(x_notrend)  
        f = fft.fftfreq(n)            
        indexes = list(range(n))
  
        indexes.sort(key = lambda i: np.absolute(f[i]))
 
        t = np.arange(0, n + n_predict)
        restored_sig = np.zeros(t.size)
        for i in indexes[:1 + n_harm * 2]:
            ampli = np.absolute(x_freqdom[i]) / n   
            phase = np.angle(x_freqdom[i])          
            restored_sig += ampli * np.cos(2 * np.pi * f[i] * t + phase)
            return restored_sig + p[0] * t

    
    
    def predict(self,timestamp,sticker,context):
        closehist = context[:,2]
        extrapolation = self.fourierExtrapolation(closehist, self.advance)
        r = extrapolation[-1] - closehist[-1]
        return r
        
        