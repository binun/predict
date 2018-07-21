from __future__ import division
from predictors.Predictor import Predictor
import numpy
from Configuration import Configuration
from Service.Utilities import Tools

from scipy import log2
#import lzma,zlib,gzip

class lzwPredictor(Predictor):
    
    conv = {1:'u',-1:'d',0:'n'}
    maxlen=7
    
    def __init__(self, dataManager,hist=-1,context=None,way='lzma'):
        super().__init__("lz",dataManager,hist)
        self.maxhistlen = 20
        self.way=way
        
    
    @staticmethod    
    def toSymbol(x):
        return lzwPredictor.conv[int(numpy.sign(x))]
    
    @staticmethod
    def toString(hist):
        return ''.join([lzwPredictor.toSymbol(hi) for hi in hist])
    
    
    
    def forecast(self,S): 
        
        data_u = (S+'u').encode()
        data_d = (S+'d').encode()
        tryUp=0
        tryDown=0
        
        if self.way=='lzma':
            tryUp = len(lzma.compress(data_u))
            tryDown = len(lzma.compress(data_d))
        
        if self.way=='zlib':
            tryUp = len(zlib.compress(data_u))
            tryDown = len(zlib.compress(data_d))
        
        if self.way=='gzip':
            tryUp = len(gzip.compress(data_u))
            tryDown = len(gzip.compress(data_d))
        
        if self.way=='huff':
            tryUp = Tools.hfcmplen(data_u)
            tryDown = Tools.hfcmplen(data_d)
        
        if tryUp==0 and tryDown==0:
            return (0,0,True)
        
        if tryUp<=tryDown:
            return (1,tryUp/(tryUp+tryDown),False)
        
        if tryUp>tryDown:
            #if tryDown/(tryUp+tryDown) > Configuration.minboldprob:
            return (-1,tryDown/(tryUp+tryDown),False)
        
        return (0,0,True)
        
    def predict(self,sticker,timestamp,context):
        
        growths=[int(numpy.sign(x)) for x in context[2]]
        S = lzwPredictor.toString(growths)
        del growths

        return self.forecast(S)
    
    def runAll(self):
        self.preprocess()
        
        
        
        