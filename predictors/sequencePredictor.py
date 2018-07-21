from predictors.Predictor import Predictor
import numpy
from Configuration import Configuration
import re

class sequencePredictor(Predictor):
    
    conv = {1:'u',-1:'d',0:''}
    maxlen=7
    
    def __init__(self, dataManager,hist=-1,context=None,fixlen=-1):
        super().__init__("seq",dataManager,hist)
        self.maxhistlen = 80
        self.rng=None
        
        if fixlen!=-1:
            self.rng=[fixlen]
            self.name=self.name+str(fixlen)
        else:
            self.rng=range(1,sequencePredictor.maxlen+1)
    @staticmethod    
    def toSymbol(x):
        return sequencePredictor.conv[int(numpy.sign(x))]
    
    @staticmethod
    def toString(hist):
        return ''.join([sequencePredictor.toSymbol(hi) for hi in hist])
    
        
    @staticmethod    
    def confidence(hist,direction,depth):
        pattern = hist[-depth:]+direction
        r=0
        n=0
        occurrences=re.finditer(pattern,hist)
        
        for occ in occurrences:
            r = r+(occ.pos+1)
            n=n+1
            
        if n==0:
            return 0
        return r
    
    
    def tryDirection(self,hist,direction,timestamp,sticker):
        s=0
        
        dirs=['d','u']
        dr = dirs.index(direction)
        for d in self.rng:
            c = sequencePredictor.confidence(hist, direction, d)
            s=s+c
            self.setUDW(timestamp,sticker,dr,c)  
        return s

    
    def forecast(self,S,timestamp,sticker): #7
        
        tryUp = self.tryDirection(S,'u',timestamp,sticker)
        tryDown = self.tryDirection(S,'d',timestamp,sticker)
       
        if (tryUp+tryDown)==0:
            return (0,(0,0),True)
        
        if tryUp>tryDown:
            
            return (1,(tryUp/(tryUp+tryDown),tryDown/(tryUp+tryDown)),False)
        if tryUp<tryDown:
        
            return (-1,(tryDown/(tryUp+tryDown),tryUp/(tryUp+tryDown)),False)
        
        return (0,(0,0),True)
    
        
    def predict(self,sticker,timestamp,context):
        
        growths=[int(numpy.sign(x)) for x in context[2]]
        S = sequencePredictor.toString(growths)
        del growths
        return self.forecast(S,timestamp,sticker)
    
    def runAll(self,since=None,until=None):
        self.preprocess(since,until)
    
    def restore(self):
        
        self.hits[0].append(0)
        self.skips[0].append(0)
        self.predictions[0].append(0)
        self.confidences[0].append(0)
        self.negconfidences[0].append(0)
        
        (c,r,x) = self.udw.shape
        udw = numpy.ones( (c,r+1,2) )
        
        for ci in range(0,c):
            for ri in range(0,r):
                udw[ci,ri]=self.udw[ci,ri]
                
        for ci in range(0,c):
            udw[ci,r] = [1,1]
        
        self.udw=udw
        
        