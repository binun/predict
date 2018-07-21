from predictors import Predictor
import numpy
import math
from Configuration import Configuration
import os
from fileinput import close

class bernoulliPredictor(Predictor.Predictor):
   
    def __init__(self, dataManager,hist=-1,stick=None,context=None):
        super().__init__("br",dataManager,hist,stick)
        
#     def nonskips(self,timestamp,sticker):
#         closehist = self.dataManager.getDataset().get(sticker,'close',timestamp,self.histlen)
#         P=self.P_n(closehist)
#         BChain=0
#         for i in range(0,len(closehist)-3):
#             y1 = int(numpy.sign(closehist[i+1]-closehist[i]))
#             y2 = int(numpy.sign(closehist[i+2]-closehist[i+1]))
#             y3 = int(numpy.sign(closehist[i+3]-closehist[i+2]))
#             
#             if (P>0.5 and y1<0 and y2>0 and y3>0) or (y1>0 and y2>0 and y3<0):
#                 BChain = BChain + 1
#             #if (Y(length(Y)-i)==1&Y(length(Y)-i-1)==1&(P_n>0.5)&Y(length(Y)-i-2)==0)|(Y(length(Y)-i)==0&Y(length(Y)-i-1)==1&Y(length(Y)-i-2)==1)
#         return BChain
    
    def runAll(self):
        self.preprocess()
            
        
        
    def P_n(self,h):
        positiv=0
            
        for i in range(0,len(h)-1):
            if h[i]<=h[i+1]:
                positiv = positiv+1
            
        p = float(positiv/(len(h)-1))
        q = 1 - p
        
        qr = math.sqrt(q*q+4*p*q)
        
        P_ = (p*p)/(4*qr)
        fd = (q+qr)*(q+qr)-(q-qr)*(q-qr)
        P_ = P_*fd
        
        #P_ = P_*(fd+sd)
        #return P_
        return p+0.1
    
    
    def predict(self,sticker,timestamp,context):
        
        closehist = context[2]
        
#         nextClose = self.dataManager.getDataset().getAt(sticker,'close',timestamp)
#         h = list(closehist)
#         h.append(nextClose)
#         P=self.P_n(h)      
#         confidence = 0
#         BPred=0
#         BChain=0
#         last = False
#         i=0
#         while i<len(closehist)-3:
#             D = self.dataManager.addDays(timestamp,-i)      # predicted day
#             D_1 = self.dataManager.addDays(timestamp,-i-1)  
#             D_2 = self.dataManager.addDays(timestamp,-i-2)
#             D_3 = self.dataManager.addDays(timestamp,-i-3)
#                  
#                  
#             C = self.dataManager.getDataset().getAt(sticker,'close',D) # predicted value
#             C_1 = self.dataManager.getDataset().getAt(sticker,'close',D_1)
#             C_2 = self.dataManager.getDataset().getAt(sticker,'close',D_2)
#             C_3 = self.dataManager.getDataset().getAt(sticker,'close',D_3)
#              
#             i=i+1
#             if C==0.0:
#                 last=True
                  
#             # if (Y(length(Y)-i)==1&Y(length(Y)-i-1)==1&(P_n>0.5)&Y(length(Y)-i-2)==0)|(Y(length(Y)-i)==0&Y(length(Y)-i-1)==1&Y(length(Y)-i-2)==1)
#         if (P>0.5 and C>=C_1 and C_1>=C_2 and C_2<C_3) or (C<C_1 and C_1>=C_2 and C_2>=C_3):
#                 #if C_>=C_1 and C_1>=C_2:
#                 BChain = BChain+1
#                  
#             if (P>=0.5 and C>=C_1 and C_1>=C_2 and C_2>=C_3) or (P<0.5 and C<C_1 and C_2>=C_1 and C_2>=C_3):
#                 BPred = BPred+1
#                  
#             if BChain>0:
#                 confidence = float(BPred/BChain)
        
        D_1 = self.dataManager.addDays(timestamp,-1)
        D_2 = self.dataManager.addDays(timestamp,-2)
        D_3 = self.dataManager.addDays(timestamp,-3)
            
        C_1 = self.dataManager.getDataset().getAt(sticker,'close',D_1)
        C_2 = self.dataManager.getDataset().getAt(sticker,'close',D_2)
        C_3 = self.dataManager.getDataset().getAt(sticker,'close',D_3)
        P=self.P_n(closehist)
        
        skip=True
        confidence=1
        decision=0
        if C_1>=C_2 and C_2>=C_3:
            skip=False
            if P>=0.5:
                decision=1
            else:
                decision=-1
            
        return (decision,confidence,skip)
        
        
        