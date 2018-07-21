from predictors import Predictor

import numpy.linalg
from Configuration import Configuration

class forexsimPredictor(Predictor.Predictor):
        
    def __init__(self, dataManager,hist=-1,stick=None,context=None):
        super().__init__("fx",dataManager,hist,stick)
    
    def runAll(self):
        self.preprocess()
    
    def predict(self,sticker,timestamp,context):
        closehist = context[2]
        n=len(closehist)
        l = int(n/3)
        x = closehist[-l:]
        A = numpy.ones( ( l, 2) ) 
        E = []
        K = [0]
        
        for i in range(0, n - l - 1):
            A[:,1] = list(closehist[i:i+l])      
            c = numpy.linalg.solve(numpy.dot(numpy.transpose(A),A), numpy.dot(numpy.transpose(A),numpy.transpose(x))) 
            nt = numpy.subtract(numpy.dot(A,c), numpy.transpose(x))
            # c = (A'*A)\(A'*x');
            e = numpy.dot(numpy.transpose(nt),nt) 
            # e = (A*c - x')'*(A*c - x')
            # nt = (A*c - x')
            E.append(e)
        
        imax = numpy.argsort(E)
        IM=imax[0]
        z = 0
        A2 = numpy.ones( (1,2) )
        
        A[:,1] = list(closehist[IM:IM+l]) 
        c = numpy.linalg.solve(numpy.dot(numpy.transpose(A),(A)), numpy.dot(numpy.transpose(A),numpy.transpose(x)) )
        # c = (A'*A)\(A'*x'); (2,1)
        A2[0,1] = closehist[IM+l]
               
        z = z + numpy.transpose(numpy.dot(A2,c))
        
        tomorrow = z
    
        confidence = 1
        prediction = numpy.sign(tomorrow)
        skip = (confidence<Configuration.minclosegap)
        return (prediction,confidence,skip)