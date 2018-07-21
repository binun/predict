from predictors.Predictor import Predictor
import numpy
from Configuration import Configuration
import re
from fileinput import close

class markovPredictor(Predictor):
   
    def __init__(self, dataManager,hist=-1,context=None):
        super().__init__("mrk",dataManager,hist)
        self.maxhistlen = 100
    
    def predict(self,sticker,timestamp,context):
        
        closehist = context[2]
        Y=[max(0,int(numpy.sign(x))) for x in context[2]]
    
        Count10=0
        Count00=0
        Count11=0
        Count01=0
                    
        for i in range(0,len(Y)-1):
            
            if Y[i]==1 and Y[i+1]==1:
                Count11 = Count11+1
                
            if Y[i]==0 and Y[i+1]==1:
                Count01 = Count01+1
            
            if Y[i]==1 and Y[i+1]==0:
                Count10 = Count10+1
            
            if Y[i]==0 and Y[i+1]==0:
                Count00 = Count00+1
    
        PT1=Count11
        PT2=Count10
        PT3=Count01
        PT4=Count00
        PT=[PT1,PT2,PT3,PT4]
        
#         if max(PT)>2.5*min(PT):
#             
#             return (0,(0,0),True)
        
        #if (Y[-1]==1 or Y[-1]==0) and PT1+PT3>PT2+PT4:
        if PT1+PT3>PT2+PT4:
            return(1,(1,1),False)
        
        #if (Y[-1]==1 or Y[-1]==0) and PT1+PT3<PT2+PT4:
        if PT1+PT3<PT2+PT4:
            #return (0,(0,0),True)
            return(-1,(1,1),False)
        
        return (0,(0,0),True)
    
    def runAll(self,until=None):
        self.preprocess(until)
        
        
        
        